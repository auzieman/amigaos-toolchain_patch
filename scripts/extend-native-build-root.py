#!/usr/bin/env python3
"""Add reviewed native build infrastructure through apt in a frozen child root.

Never edits the parent template or runs target binaries. Debian apt performs
installation; checks retain baseline versions and ordinary configured state.
"""
import argparse, hashlib, json, os, subprocess
from pathlib import Path
from apt_archive_cache import prepare as prepare_cache, retain as retain_cache
p=argparse.ArgumentParser(description=__doc__)
for key in ['project','base','output']:p.add_argument('--'+key,type=Path,required=True)
p.add_argument('--parent-receipt',type=Path)
p.add_argument('--parent-sha256')
p.add_argument('--metadata-receipt',type=Path)
p.add_argument('--metadata-sha256')
p.add_argument('--include-native',nargs='+',required=True)
a=p.parse_args();assert a.output.resolve().is_relative_to((a.base/'work').resolve());a.output.mkdir(exist_ok=False)
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
spec=json.loads((a.project/'profiles/sbuild/libx11.json').read_text())
lockpath=a.project/spec['base_lock'];lock=json.loads(lockpath.read_text())
assert bool(a.parent_receipt)==bool(a.parent_sha256)
parent=a.parent_receipt or a.base/spec['native_root_receipt']
assert sha(parent)==(a.parent_sha256 or spec['native_root_receipt_sha256'])
previous=json.loads(parent.read_text());assert previous['status']=='native-buildd-root-created'
assert previous['base_lock_sha256']==sha(lockpath)
archive=parent.parent/'trixie-amd64.tar';assert sha(archive)==previous['sha256']
root=a.output/'root';root.mkdir()
cache_base=a.base.parent.parent/'tabor-apt-cache'
cache=prepare_cache(cache_base,a.output.name,parent.parent/'root/var/cache/apt/archives',0,0)
r={'status':'preparing','base_lock_sha256':sha(lockpath),'parent_receipt_sha256':sha(parent),
   'recipe_sha256':sha(Path(__file__)),'native_additions':a.include_native,'target_execution':False}
def save():(a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
def run(cmd,name):
 with (a.output/(name+'.log')).open('w') as log:
  result=subprocess.run(list(map(str,cmd)),stdout=log,stderr=subprocess.STDOUT)
 assert result.returncode==0,name+' failed'
def inside(cmd,name):
 run(['systemd-nspawn','--quiet','--register=no','--timezone=off','--as-pid2',
      '--bind='+str(cache)+':/var/cache/apt/archives','--directory='+str(root),'--setenv=DEBIAN_FRONTEND=noninteractive',*cmd],name)
try:
 save();run(['tar','--numeric-owner','-xf',archive,'-C',root],'extract')
 if a.metadata_receipt:
  assert a.metadata_sha256 and sha(a.metadata_receipt)==a.metadata_sha256
  metadata=json.loads(a.metadata_receipt.read_text());assert metadata['base_lock_sha256']==sha(lockpath) and metadata['status']=='native-buildd-root-created'
  run(['cp','-a',str(a.metadata_receipt.parent/'root/var/lib/apt/lists')+'/.',root/'var/lib/apt/lists'],'reuse-frozen-apt-indexes')
  r['metadata_receipt_sha256']=a.metadata_sha256
 (root/'etc/apt/apt.conf.d/80tabor-download-retries').write_text('Acquire::Retries "5";\n')
 (root/'etc/apt/apt.conf.d/90port-package-cache').write_text('APT::Keep-Downloaded-Packages "true";\nBinary::apt-get::APT::Keep-Downloaded-Packages "true";\n')
 inside(['apt-get','update'],'apt-update')
 assert all(x.replace('-','').isalnum() for x in a.include_native)
 inside(['apt-get','--no-remove','--no-install-recommends','-y','install',*[x+':amd64' for x in a.include_native]],'install-native-infrastructure')
 inside(['apt-get','check'],'apt-check')
 inside(['dpkg','--audit'],'dpkg-audit');assert not (a.output/'dpkg-audit.log').read_text().strip()
 installed={}
 for para in (root/'var/lib/dpkg/status').read_text().split('\n\n'):
  fields=dict(line.split(': ',1) for line in para.splitlines() if ': ' in line and not line.startswith(' '))
  if fields.get('Status')=='install ok installed':installed[fields['Package']]=fields['Version']
 for name,version in lock['native_foundation'].items():assert installed.get(name)==version,(name,installed.get(name),version)
 assert all(name in installed for name in a.include_native)
 solver=root/'usr/lib/apt/solvers/apt';assert solver.is_file() and os.access(solver,os.X_OK)
 r['apt_cross_solver_sha256']=sha(solver)
 inventory=a.output/'installed-versions.json';inventory.write_text(json.dumps(installed,indent=2)+'\n')
 target=a.output/'trixie-amd64.tar';run(['tar','--numeric-owner','-cf',target,'-C',root,'.'],'archive')
 r.update(status='native-buildd-root-created',sha256=sha(target),installed_versions_sha256=sha(inventory),installed_packages=len(installed))
except Exception as error:
 r.update(status='failed',error=str(error));raise
finally:
 r['apt_archive_cache']=retain_cache(cache_base,cache)
 save()
