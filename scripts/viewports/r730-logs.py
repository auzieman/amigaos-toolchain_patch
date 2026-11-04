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
 if not active:return 'R730 BUILD LOGS — no active package pipeline\nRetained completed logs are not running jobs.'
 root=max(active,key=lambda p:p.stat().st_mtime);prefix=root.parent.name
 receipts=list((base/'work').glob(prefix+'-*/receipt.json'));running=[];completed=[]
 for p in receipts:
  r=load(p)
  if r.get('status')=='sbuild-running':running.append((p,r))
  elif r.get('status') in ['failed','debian-packages-built-not-target-installed']:completed.append((p,r))
 lines=['R730 BUILD LOGS — '+prefix,'Refresh: 4s | server-side bounded tails | '+str(len(running))+' running jobs','']
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
