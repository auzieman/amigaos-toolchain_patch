#!/usr/bin/env python3
"""Build the real dependency-only crossbuild-essential SPE port adapter."""
import argparse,hashlib,json,os,pwd,shutil,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for n in ['project','output']:p.add_argument('--'+n,type=Path,required=True)
a=p.parse_args();a.output.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=a.project/'packaging/tabor-spe-cross-build-essential';tree=a.output/'source';shutil.copytree(source,tree)
r={'status':'preparing','package':'tabor-spe-cross-build-essential','method':'Native architecture-independent Debian port metapackage source build','target_execution':False,'target_installation':False,'boot_image_ready':False,'source_files':{str(p.relative_to(source)):sha(p) for p in source.rglob('*') if p.is_file()},'packages':{}}
try:
 owner=pwd.getpwnam('owner')
 for pth in [a.output,*a.output.rglob('*')]:os.chown(pth,owner.pw_uid,owner.pw_gid)
 cmd=['runuser','-u','owner','--','dpkg-buildpackage','--build=source,all','-us','-uc']
 with (a.output/'build.log').open('w') as log:
  assert subprocess.run(cmd,cwd=tree,stdout=log,stderr=subprocess.STDOUT).returncode==0
 for f in a.output.glob('*.deb'):
  assert subprocess.check_output(['dpkg-deb','-f',f,'Architecture'],text=True).strip()=='all'
  r['packages'][f.name]={'sha256':sha(f),'bytes':f.stat().st_size}
 assert len(r['packages'])==1
 r['build_metadata']={f.name:sha(f) for pattern in ['*.dsc','*.tar.xz','*.changes','*.buildinfo'] for f in a.output.glob(pattern)}
 r['status']='debian-packages-built-not-target-installed'
 (a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
 with (a.output/'payload-inspection.log').open('w') as log:
  assert subprocess.run(['python3',a.project/'scripts/inspect-spe-package-payloads.py','--receipt',a.output/'receipt.json','--output',a.output/'payload-inspection.json'],stdout=log,stderr=subprocess.STDOUT).returncode==0
 r['payload_inspection_sha256']=sha(a.output/'payload-inspection.json')
except BaseException as error:r.update(status='failed',error=str(error));raise
finally:(a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
