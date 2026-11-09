from pathlib import Path
import json,hashlib,lzma,subprocess,os
from debian.deb822 import Sources
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
b=Path('/srv/data1/tabor-build/linux-live-001');meta=b/'work/wide-desktop-dependency-probes-002';d=json.loads((meta/'receipt.json').read_text());assert d['status']=='wide-desktop-dependency-probes-completed'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();sources={}
for i,index in enumerate(d['source_indexes']):
 p=meta/(str(i)+'-Sources.xz');assert sha(p)==index['sha256']
 with lzma.open(p,'rt') as f:
  for s in Sources.iter_paragraphs(f,use_apt_pkg=False):
   if s['Package'] in ['piglit','waffle']:sources[s['Package']]=s
assert set(sources)=={'piglit','waffle'}
w=b/'work/piglit-standard-20261109-001';w.mkdir(exist_ok=False);cache=b/'hardware-test-source-cache';cache.mkdir(exist_ok=True);result={}
for name,s in sources.items():
 files=[]
 for x in s['Checksums-Sha256']:
  n=x['name'];assert Path(n).name==n;f=cache/n;url='https://deb.debian.org/debian/'+s['Directory']+'/'+n
  if not f.exists():
   t=cache/(n+'.partial');subprocess.run(['curl','--fail','--location','--retry','3','--retry-delay','2','--max-time','90','--silent','--show-error',url,'-o',str(t)],check=True);assert sha(t)==x['sha256'] and t.stat().st_size==int(x['size']);t.rename(f)
  assert sha(f)==x['sha256'];files.append({'file':str(f),'sha256':sha(f),'url':url})
 dsc=next(x['file'] for x in files if x['file'].endswith('.dsc'));subprocess.run(['dpkg-source','--no-check','-x',dsc,str(w/name)],check=True)
 result[name]={'version':s['Version'],'files':files,'build_depends':s.get('Build-Depends')}
(w/'intake.json').write_text(json.dumps({'sources':result,'metadata_receipt_sha256':sha(meta/'receipt.json'),'base_lock_sha256':d['base_lock_sha256'],'purpose':'standard unmodified test-suite diagnostic; not target package acceptance'},indent=2)+'\n');print(json.dumps({k:v['version'] for k,v in result.items()}))
