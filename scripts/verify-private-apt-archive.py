#!/usr/bin/env python3
"""Check signed powerpcspe indexes and dependency closure using host apt, without native coinstallation."""
import argparse,hashlib,json,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--seed-profile',type=Path,help='Also simulate the boot installation seed closure')
p.add_argument('--archive',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--image-id',required=True)
a=p.parse_args();a.output.mkdir(exist_ok=False)
for n in ['lists','sourceparts']:(a.output/n).mkdir()
(a.output/'target-status').write_text('')
# Empty bootstrap database: no installed package records are invented.
# This simulates target dependencies; it does not configure or execute packages.
options=['-o','APT::Architecture=powerpcspe','-o','APT::Architectures=powerpcspe','-o','Dir::State::status='+str(a.output/'target-status'),'-o','Dir::Etc::sourcelist='+str(a.archive/'tabor.sources'),'-o','Dir::Etc::sourceparts='+str(a.output/'sourceparts'),'-o','Dir::State::lists='+str(a.output/'lists'),'-o','Acquire::Languages=none']
r={'status':'started','image_id':a.image_id,'archive_receipt_sha256':hashlib.sha256((a.archive/'receipt.json').read_bytes()).hexdigest(),'target_installation':False,'boot_image_ready':False,'tests':{}}
commands={'update':['apt-get',*options,'update'],
 'policy':['apt-cache',*options,'policy','libc6:powerpcspe','libcap-ng0:powerpcspe','libsepol2:powerpcspe','libpcre2-8-0:powerpcspe'],
 'install-simulation':['apt-get',*options,'--simulate','--no-install-recommends','install','libc6:powerpcspe','libsepol-dev:powerpcspe','libpcre2-dev:powerpcspe','libcap-ng-dev:powerpcspe']}
if a.seed_profile:
 seeds=json.loads(a.seed_profile.read_text())['package_seeds']['installation']
 commands['essential-simulation']=['apt-get',*options,'--simulate','--no-install-recommends','install',*seeds]
try:
 for name,cmd in commands.items():
  t=subprocess.run(cmd,text=True,capture_output=True)
  (a.output/(name+'.log')).write_text(t.stdout+t.stderr)
  r['tests'][name]={'command':cmd,'exit':t.returncode,'log_sha256':hashlib.sha256((t.stdout+t.stderr).encode()).hexdigest()}
  if name not in ['install-simulation','essential-simulation']:assert t.returncode==0, name
  if name=='policy':
   for pkg in ['libc6:powerpcspe','libcap-ng0:powerpcspe','libsepol2:powerpcspe','libpcre2-8-0:powerpcspe']:assert pkg.split(':')[0]+':' in t.stdout
 if a.seed_profile:r['essential_closure_ready']=r['tests']['essential-simulation']['exit']==0
 r['status']='archive-verified-selected-dependencies-'+('ready' if r['tests']['install-simulation']['exit']==0 else 'blocked')
finally:(a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
print(r['status'])
