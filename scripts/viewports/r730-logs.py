"""Bounded current sbuild tails, rendered on the server every four seconds."""
from pathlib import Path
import json,os,re,sys,time
base=Path('/srv/data1/tabor-build/linux-live-001');script=Path(__file__);stamp=script.stat().st_mtime_ns
last=None
def load(p):
 try:return json.loads(p.read_text())
 except (OSError,ValueError):return {}
def render():
 roots=[p for p in (base/'work').glob('port-*/receipt.json') if re.fullmatch(r'port-(?:pipeline|qualification)-\d{8}-\d+',p.parent.name)]
 active=[p for p in roots if load(p).get('status')=='running']
 if not roots:return 'R730 BUILD LOGS — no retained pipeline receipts'
 root=max(active or roots,key=lambda p:p.stat().st_mtime);prefix=root.parent.name
 receipts=list((base/'work').glob(prefix+'-*/receipt.json'));running=[];completed=[]
 for p in receipts:
  r=load(p)
  if r.get('status')=='sbuild-running':running.append((p,r))
  elif r.get('status') in ['failed','debian-packages-built-not-target-installed']:completed.append((p,r))
 passed=[(p,r) for p,r in completed if r.get('payload_inspection_sha256')]
 lines=['R730 BUILD LOGS — '+prefix,load(root).get('status','unknown')+' | '+str(len(running))+' running | '+str(len(passed))+' new source builds / '+str(sum(len(r.get('packages',{})) for p,r in passed))+' .debs','Refresh: 4s; completed results remain visible.','']
 if not running:
  lines.extend(r.get('package',p.parent.name)+' — PASS ('+str(len(r.get('packages',{})))+' .debs)' for p,r in passed)
  fallout=load(root.parent/'fallout.json')
  blocked={x.get('package') for x in fallout if x.get('package')} if isinstance(fallout,list) else set()
  lines.extend(['',str(len(blocked))+' sources deferred; dependency/bootstrap/foundation work remains.',', '.join(sorted(blocked))[:450]])
  failures=[r for p,r in completed if r.get('status')=='failed']
  lines.extend(r.get('package','?')+' — FAILED: '+r.get('error','see retained log')[:120] for r in failures[:4])
  if completed:return '\n'.join(lines)
 selected=running[:4] or sorted(completed,key=lambda x:x[0].stat().st_mtime,reverse=True)[:3]
 if not selected:lines.append('Dependency audit / source preparation; no compiler job active yet.')
 for p,r in selected:
  lines.append(r.get('package',p.parent.name)+' — '+r['status'])
  log=p.parent/'sbuild.log'
  if log.exists():
   with log.open('rb') as f:
    f.seek(max(0,log.stat().st_size-4000));tail=f.read().decode(errors='replace').splitlines()[-3:]
   lines.extend(line[:150] for line in tail)
  lines.append('')
 return '\n'.join(lines)
try:
 while True:
  if script.stat().st_mtime_ns!=stamp:os.execv(sys.executable,[sys.executable,str(script),*sys.argv[1:]])
  content=render()
  if content!=last:print(('' if '--once' in sys.argv else '\033[H\033[2J')+content,flush=True);last=content
  if '--once' in sys.argv:break
  time.sleep(4)
except KeyboardInterrupt:pass
