#!/usr/bin/env python3
"""Create one snapshot-pinned native Debian buildd root; never refresh versions."""
import argparse, hashlib, json, subprocess, tarfile
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--lock',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args(); lock=json.loads(a.lock.read_text());a.output.mkdir(exist_ok=False)
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
root=a.output/'trixie-amd64.tar'
mirrors=['deb [check-valid-until=no] '+item['url']+' '+item['suite']+' main' for item in lock['repositories']]
cmd=['mmdebstrap','--variant=buildd','--architectures=amd64','--include=ca-certificates,apt-utils','--format=tar','trixie',str(root),*mirrors]
r={'status':'preparing','command':cmd,'base_lock_sha256':sha(a.lock),'target_execution':False}
try:
 with (a.output/'mmdebstrap.log').open('w') as log:
  r['exit']=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT).returncode
 assert r['exit']==0,'mmdebstrap failed; inspect log'
 with tarfile.open(root) as t:
  member=next(x for x in t if x.name.lstrip('./')=='var/lib/dpkg/status')
  status=t.extractfile(member).read().decode()
 packages={}
 for paragraph in status.split('\n\n'):
  fields=dict(line.split(': ',1) for line in paragraph.splitlines() if ': ' in line and not line.startswith(' '))
  if fields.get('Status')=='install ok installed':packages[fields['Package']]=fields['Version']
 assert 'apt-utils' in packages, 'Debian cross resolver requires native apt-utils'
 for name,version in lock['native_foundation'].items():
  assert packages.get(name)==version,(name,packages.get(name),version)
 (a.output/'installed-versions.json').write_text(json.dumps(packages,indent=2)+'\n')
 r.update(status='native-buildd-root-created',sha256=sha(root),installed_versions_sha256=sha(a.output/'installed-versions.json'))
except Exception as e:
 r.update(status='failed',error=str(e));raise
finally:(a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
