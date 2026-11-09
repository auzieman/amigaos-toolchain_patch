from pathlib import Path
import json,hashlib,lzma,subprocess,os
from debian.deb822 import Sources
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
b=Path('/srv/data1/tabor-build/linux-live-001');meta=b/'work/wide-desktop-dependency-probes-002';d=json.loads((meta/'receipt.json').read_text());assert d['status']=='wide-desktop-dependency-probes-completed'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
src=None
for i,index in enumerate(d['source_indexes']):
 p=meta/(str(i)+'-Sources.xz');assert sha(p)==index['sha256']
 with lzma.open(p,'rt') as f:
  for s in Sources.iter_paragraphs(f,use_apt_pkg=False):
   if s['Package']=='kmscube':
    assert s['Version']=='0.0.0~git20210103-1';src=s
assert src
cache=b/'hardware-test-source-cache';cache.mkdir(exist_ok=True);w=b/'work/kmscube-intake-20261109-001';w.mkdir(exist_ok=False);files=[]
for x in src['Checksums-Sha256']:
 n=x['name'];assert Path(n).name==n;f=cache/n;url='https://deb.debian.org/debian/'+src['Directory']+'/'+n
 if not f.exists():
  temp=cache/(n+'.partial');subprocess.run(['curl','--fail','--location','--retry','3','--retry-delay','2','--max-time','60','--silent','--show-error',url,'-o',str(temp)],check=True);assert sha(temp)==x['sha256'] and temp.stat().st_size==int(x['size']);temp.rename(f)
 assert sha(f)==x['sha256'];files.append({'file':str(f),'sha256':sha(f),'url':url})
dsc=next(x['file'] for x in files if x['file'].endswith('.dsc'));subprocess.run(['dpkg-source','--no-check','-x',dsc,str(w/'source')],check=True)
(w/'receipt.json').write_text(json.dumps({'version':src['Version'],'source_indexes_receipt_sha256':sha(meta/'receipt.json'),'base_lock_sha256':d['base_lock_sha256'],'files':files,'source_unpacked':True,'target_execution':False},indent=2)+'\n');print('Frozen Trixie kmscube source cached and SHA-verified')
