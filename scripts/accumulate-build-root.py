#!/usr/bin/env python3
"""Install receipt-pinned coinstallable SPE libraries into a new build image.

This is cross-build infrastructure, not target image promotion. Debian apt
checks dependencies, versions and shared files. Native tools are not replaced.
Only Multi-Arch:same target packages are eligible; data/tools need explicit
separate review. Failed transactions retain the prior immutable image.
"""
import argparse, hashlib, json, os, re, subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for key in ['project','base','receipt','output']: p.add_argument('--'+key,type=Path,required=True)
p.add_argument('--parent-image',required=True)
a=p.parse_args()
assert re.fullmatch(r'sha256:[0-9a-f]{64}',a.parent_image)
assert a.receipt.resolve().is_relative_to((a.base/'work').resolve())
assert a.output.resolve().is_relative_to((a.base/'work').resolve())
a.output.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original=json.loads(a.receipt.read_text())
assert original['status']=='debian-packages-built-not-target-installed'
assert original.get('package_managed_root') and original.get('preserve_debian_version')
assert not original.get('build_root_only')
r={'status':'running','parent_image':a.parent_image,'image_id':a.parent_image,
   'receipt_sha256':sha(a.receipt),'recipe_sha256':sha(Path(__file__)),
   'selected':[],'excluded':[],'target_installation':False}
def run(cmd,name):
 with (a.output/(name+'.log')).open('w') as log:
  subprocess.run(list(map(str,cmd)),stdout=log,stderr=subprocess.STDOUT,check=True,
                 env={**os.environ,'DOCKER_BUILDKIT':'0'})
try:
 for name,entry in original['packages'].items():
  if not name.endswith('.deb'):continue
  assert Path(name).name==name
  f=a.receipt.parent/name;assert sha(f)==entry['sha256']
  meta={}
  for field in ['Package','Architecture','Multi-Arch','Version']:
   meta[field]=subprocess.check_output(['dpkg-deb','-f',str(f),field],text=True).strip()
  if meta['Architecture']=='powerpcspe' and meta['Multi-Arch']=='same' and not meta['Package'].endswith('-dbgsym'):
   r['selected'].append({**meta,'file':name,'sha256':entry['sha256']})
  else:r['excluded'].append(meta)
 if not r['selected']:
  r['status']='no-coinstallable-library-packages'
 else:
  run(['python3',a.project/'scripts/inspect-spe-package-payloads.py','--receipt',a.receipt,
       '--output',a.output/'payload-inspection.json'],'payload-inspection')
  installed=subprocess.check_output(['docker','run','--rm','--network=none','--cpus=1','--memory=512m',
    '--pids-limit=64','--entrypoint','dpkg-query',a.parent_image,'-W',
    '-f=${Package}\t${Architecture}\t${Version}\t${db:Status-Status}\n'],text=True)
  present={tuple(line.split('\t')[:3]) for line in installed.splitlines() if line.endswith('\tinstalled')}
  if all((m['Package'],m['Architecture'],m['Version']) in present for m in r['selected']):
   r['status']='already-installed'
  else:
   manifest={'purpose':'Cumulative managed cross-build dependency feedback; not final target installation',
     'inputs':[{'receipt':str(a.receipt.relative_to(a.base)), 'receipt_sha256':sha(a.receipt),
                'packages':[m['Package'] for m in r['selected']]}]}
   (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
   context=a.output/'context'
   run(['python3',a.project/'scripts/prepare-target-build-context.py','--base',a.base,
       '--manifest',a.output/'manifest.json','--dockerfile',a.project/'docker/Dockerfile.target-development',
       '--output',context],'prepare')
   # Keep the existing normal-install recipe; prevent removals; Docker network isolation prohibits fetches.
   df=context/'Dockerfile';s=df.read_text().replace('apt-get install -y --no-install-recommends',
        'apt-get install -y --no-remove --no-install-recommends')
   df.write_text(s)
   run(['docker','build','--network=none','--cpuset-cpus=0-3','--memory=6g',
       '--build-arg','BUILD_INFRA_IMAGE='+a.parent_image,'--iidfile',a.output/'image.id',context],'install')
   image=(a.output/'image.id').read_text().strip();assert re.fullmatch(r'sha256:[0-9a-f]{64}',image)
   # Verify that an apt dependency solution has not changed native packages.
   after=subprocess.check_output(['docker','run','--rm','--network=none','--cpus=1','--memory=512m',
     '--pids-limit=64','--entrypoint','dpkg-query',image,'-W',
     '-f=${Package}\t${Architecture}\t${Version}\t${db:Status-Status}\n'],text=True)
   native=lambda data:sorted(x for x in data.splitlines() if '\tamd64\t' in x)
   assert native(installed)==native(after),'Native package state changed; image not accepted'
   r.update(status='target-libraries-installed-in-build-root',image_id=image)
except Exception as e:
 r.update(status='installation-deferred',error=str(e))
finally:
 (a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
print(r['status'],flush=True)
if r['status']=='installation-deferred':raise SystemExit(1)
