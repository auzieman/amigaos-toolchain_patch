#!/usr/bin/env python3
"""Cache exact E desktop seed sources from inspected VM132 reference metadata."""
import argparse,hashlib,json,re,urllib.request
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for n in ['reference','cache','output']:p.add_argument('--'+n,type=Path,required=True)
a=p.parse_args();reference=json.loads(a.reference.read_text())
assert reference['reference_only'] and reference['reference_architecture']=='amd64'
a.output.mkdir(parents=True,exist_ok=False);a.cache.mkdir(parents=True,exist_ok=True)
sha=lambda f:hashlib.file_digest(f.open('rb'),'sha256').hexdigest()
lock={'role':'Exact source seeds, not a resolved target dependency closure',
      'reference_sha256':sha(a.reference),'signature_verification':'not performed; HTTPS DSC plus payload hashes',
      'components':{}}
try:
 for name in ['efl','e17','terminology']:
  version=reference['sources'][name];filename=name+'_'+version.split(':')[-1]+'.dsc'
  base='https://deb.debian.org/debian/pool/main/'+name[0]+'/'+name+'/'
  dsc=a.cache/filename
  if not dsc.exists():
   with urllib.request.urlopen(base+filename,timeout=60) as src:dsc.write_bytes(src.read())
  text=dsc.read_text();assert '\nSource: '+name+'\n' in '\n'+text
  assert '\nVersion: '+version+'\n' in '\n'+text
  checksum=re.search(r'^Checksums-Sha256:\n((?: [^\n]+\n)+)',text,re.M);assert checksum
  files=[{'filename':filename,'url':base+filename,'size':dsc.stat().st_size,'sha256':sha(dsc)}]
  for line in checksum[1].splitlines():
   expected,size,archive=line.split();size=int(size)
   assert Path(archive).name==archive and re.fullmatch('[0-9a-f]{64}',expected)
   dest=a.cache/archive
   if not dest.exists():
    partial=dest.with_suffix(dest.suffix+'.partial')
    with urllib.request.urlopen(base+archive,timeout=60) as src,partial.open('xb') as out:
     while chunk:=src.read(1024**2):out.write(chunk)
    assert partial.stat().st_size==size and sha(partial)==expected,archive
    partial.rename(dest)
   assert dest.stat().st_size==size and sha(dest)==expected,archive
   files.append({'filename':archive,'url':base+archive,'size':size,'sha256':expected})
  lock['components'][name]={'version':version,'dsc':filename,'files':files,'license_review':'pending source/copyright inspection'}
  print('Verified source seed',name,version,flush=True)
 lock['status']='source-seeds-cached-and-payload-hashes-verified'
except Exception as error:
 lock.update(status='failed',error=str(error));raise
finally:(a.output/'sources.lock.json').write_text(json.dumps(lock,indent=2)+'\n')
