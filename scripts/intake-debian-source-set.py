#!/usr/bin/env python3
"""Cache an explicit source/version set through authenticated Debian apt metadata.

Run in an isolated native container; no compilation or target execution.
"""
import argparse, hashlib, json, shutil, subprocess
from pathlib import Path
from debian.deb822 import Deb822
p=argparse.ArgumentParser(description=__doc__)
for name in ['manifest','cache','output']:p.add_argument('--'+name,type=Path,required=True)
a=p.parse_args();spec=json.loads(a.manifest.read_text())
a.cache.mkdir(exist_ok=False);a.output.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=Path('/etc/apt/sources.list.d/tabor-intake.sources')
assert not source.exists()
configured=[]
for f in Path('/etc/apt/sources.list.d').glob('*.sources'):
    configured.extend(Deb822.iter_paragraphs(f.open()))
keys={x['Signed-By'] for x in configured if 'trixie' in x.get('Suites','').split()
      and 'deb.debian.org/debian' in x.get('URIs','') and 'Signed-By' in x}
assert len(keys)==1, 'Reuse the existing Debian source trust configuration'
key=keys.pop();assert Path(key).is_file()
source.write_text('Types: deb-src\nURIs: https://deb.debian.org/debian\nSuites: trixie\nComponents: main\nSigned-By: '+key+'\n')
subprocess.run(['apt-get','update'],check=True)
r={'status':'running','recipe_sha256':sha(Path(__file__)),'manifest_sha256':sha(a.manifest),
   'target_execution':False,'components':{}}
lock={'scope':spec['scope'],'signature_verification':'apt authenticated Release/Sources checksums; separate DSC signer verification not performed','components':{}}
try:
 for name,item in spec['components'].items():
  version=item['version']
  records=list(Deb822.iter_paragraphs(subprocess.check_output(['apt-cache','showsrc',name],text=True)))
  records=[x for x in records if x['Package']==name and x['Version']==version]
  assert len(records)==1,(name,version,len(records))
  record=records[0];(a.output/(name+'-source-index.txt')).write_text(str(record))
  subprocess.run(['apt-get','source','--download-only','--only-source',name+'='+version],cwd=a.cache,check=True)
  files=[]
  for line in record['Checksums-Sha256'].splitlines():
   if not line.strip():continue
   digest,size,filename=line.split();assert Path(filename).name==filename
   f=a.cache/filename;assert f.stat().st_size==int(size) and sha(f)==digest
   files.append({'filename':filename,'url':'https://deb.debian.org/debian/'+record['Directory']+'/'+filename,'size':int(size),'sha256':digest})
  dsc=next(x['filename'] for x in files if x['filename'].endswith('.dsc'))
  lock['components'][name]={'version':version,'dsc':dsc,'files':files}
  tree=a.output/(name+'-source')
  subprocess.run(['dpkg-source','--no-check','-x',a.cache/dsc,tree],check=True)
  copyright_file=tree/'debian/copyright'
  shutil.copyfile(copyright_file,a.output/(name+'-copyright.txt'))
  r['components'][name]={'version':version,'reason':item['reason'],'copyright_sha256':sha(copyright_file),'source_index_sha256':sha(a.output/(name+'-source-index.txt'))}
 (a.output/'sources.lock.json').write_text(json.dumps(lock,indent=2)+'\n')
 r['release_files']={f.name:sha(f) for f in Path('/var/lib/apt/lists').glob('*InRelease')}
 r['lock_sha256']=sha(a.output/'sources.lock.json');r['status']='sources-cached-verified-license-review-pending'
finally:
 (a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
