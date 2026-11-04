#!/usr/bin/env python3
"""Add reviewed native build infrastructure through apt in a frozen child root.

Never edits the parent template or runs target binaries. Debian apt performs
installation; checks retain baseline versions and ordinary configured state.
"""
import argparse, hashlib, json, os, subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for key in ['project','base','output']:p.add_argument('--'+key,type=Path,required=True)
p.add_argument('--include-native',nargs='+',required=True)
a=p.parse_args();assert a.output.resolve().is_relative_to((a.base/'work').resolve());a.output.mkdir(exist_ok=False)
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
spec=json.loads((a.project/'profiles/sbuild/libx11.json').read_text())
lockpath=a.project/spec['base_lock'];lock=json.loads(lockpath.read_text())
parent=a.base/spec['native_root_receipt'];assert sha(parent)==spec['native_root_receipt_sha256']
previous=json.loads(parent.read_text());assert previous['status']=='native-buildd-root-created'
assert previous['base_lock_sha256']==sha(lockpath)
archive=parent.parent/'trixie-amd64.tar';assert sha(archive)==previous['sha256']
root=a.output/'root';root.mkdir()
r={'status':'preparing','base_lock_sha256':sha(lockpath),'parent_receipt_sha256':sha(parent),
   'recipe_sha256':sha(Path(__file__)),'native_additions':a.include_native,'target_execution':False}
def save():(a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
def run(cmd,name):
 with (a.output/(name+'.log')).open('w') as log:
  result=subprocess.run(list(map(str,cmd)),stdout=log,stderr=subprocess.STDOUT)
 assert result.returncode==0,name+' failed'
def inside(cmd,name):
 run(['systemd-nspawn','--quiet','--register=no','--timezone=off','--as-pid2',
      '--directory='+str(root),'--setenv=DEBIAN_FRONTEND=noninteractive',*cmd],name)
try:
 save();run(['tar','--numeric-owner','-xf',archive,'-C',root],'extract')
 (root/'etc/apt/apt.conf.d/80tabor-download-retries').write_text('Acquire::Retries "5";\n')
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
finally:save()
