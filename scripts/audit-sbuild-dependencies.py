#!/usr/bin/env python3
"""Ask Debian dose-builddebcheck for cross-build installability and dependency trees.

Use authenticated frozen native indexes and real receipt-pinned SPE packages.
This is metadata-only: it neither compiles nor installs/executes target programs.
"""
import argparse, hashlib, json, lzma, shutil, subprocess
from pathlib import Path
from debian.deb822 import Dsc, Release, Packages
import yaml
p=argparse.ArgumentParser(description=__doc__)
for n in ['project','base','output']:p.add_argument('--'+n,type=Path,required=True)
p.add_argument('--reuse-native-audit',type=Path)
a=p.parse_args();a.output.mkdir(exist_ok=False)
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def capture(cmd):return subprocess.check_output(list(map(str,cmd)),text=True)
profile=json.loads((a.project/'profiles/images/debian-package-builder.json').read_text())
base_lock=json.loads((a.project/'profiles/trixie-spe-base.lock.json').read_text())
defaults=json.loads((a.project/'profiles/sbuild/libx11.json').read_text())
r={'status':'preparing','target_execution':False,'base_lock_sha256':sha(a.project/'profiles/trixie-spe-base.lock.json'),'indexes':[],'missing_sources':[]}
try:
 native=a.output/'NativePackages'
 if a.reuse_native_audit:
  previous=json.loads((a.reuse_native_audit/'receipt.json').read_text())
  assert previous['status']=='debian-dependency-audit-completed' and previous['base_lock_sha256']==r['base_lock_sha256']
  assert sha(a.reuse_native_audit/'NativePackages')==previous['native_packages_sha256']
  shutil.copyfile(a.reuse_native_audit/'NativePackages',native);r['indexes']=previous['indexes']
  r['native_index_receipt_sha256']=sha(a.reuse_native_audit/'receipt.json')
 else:
  with native.open('wb') as combined:
   for i,repo in enumerate(base_lock['repositories']):
    prefix=repo['url']+'dists/'+repo['suite']+'/'
    release=a.output/(str(i)+'-InRelease')
    subprocess.run(['curl','--fail','--location','--retry','2','--max-time','120','--silent','--show-error',prefix+'InRelease','-o',release],check=True)
    with (a.output/(str(i)+'-signature.log')).open('w') as log:
     subprocess.run(['gpgv','--keyring','/usr/share/keyrings/debian-archive-keyring.gpg',release],stdout=log,stderr=subprocess.STDOUT,check=True)
    record=Release(release.open())
    entry=next(x for x in record['SHA256'] if x['name']=='main/binary-amd64/Packages.xz')
    archive=a.output/(str(i)+'-Packages.xz')
    subprocess.run(['curl','--fail','--location','--retry','2','--max-time','120','--silent','--show-error',prefix+entry['name'],'-o',archive],check=True)
    assert sha(archive)==entry['sha256'] and archive.stat().st_size==int(entry['size'])
    with lzma.open(archive,'rb') as source:shutil.copyfileobj(source,combined)
    combined.write(b'\n')
    r['indexes'].append({'url':prefix,'inrelease_sha256':sha(release),'packages_sha256':sha(archive)})
 r['native_packages_sha256']=sha(native)
 # Gather real successful source-build outputs, not guessed package identities.
 selected={};records={}
 candidates=list(a.base.glob('work/*/receipt.json'))
 explicit_specs={str(a.base/x['receipt']):x for x in defaults['extra_receipts']}
 explicit=set(explicit_specs)
 libc_inputs={str(a.base/x['receipt']) for x in defaults['extra_receipts'] if 'libc6' in x['packages']}
 assert len(libc_inputs)==1, 'Use exactly the reviewed frozen libc input'
 for path in sorted(candidates,key=lambda p:p.stat().st_mtime):
  try:record=json.loads(path.read_text())
  except (ValueError,OSError):continue
  if record.get('status')!='debian-packages-built-not-target-installed':continue
  if record.get('package')=='glibc' and str(path) not in libc_inputs:continue
  if record.get('package') not in profile['packages'] and str(path) not in explicit:continue
  for name,item in record.get('packages',{}).items():
   if not name.endswith('.deb') or name.split('_')[0] in ['libgcc-s1','libstdc++6']:continue
   if record.get('package') not in profile['packages'] and name.split('_')[0] not in explicit_specs[str(path)]['packages']:continue
   f=path.parent/name
   assert f.resolve().is_relative_to(a.base.resolve()) and sha(f)==item['sha256']
   selected[name]=(path,f,record)
 grouped={};binaries=a.output/'SpePackages';artifact_names=set();artifacts=[]
 with binaries.open('w') as out:
  for name,(path,f,record) in sorted(selected.items()):
   text=capture(['dpkg-deb','-f',f]);fields=Dsc(text.splitlines())
   assert fields['Architecture'] in ['all','powerpcspe']
   out.write(text.strip()+'\n\n');artifact_names.add(fields['Package'])
   key=str(path.relative_to(a.base))
   item=grouped.setdefault(key,{'receipt':key,'sha256':sha(path),'packages':[]})
   item['packages'].append(fields['Package'])
   artifacts.append({'receipt':key,'file':name,'package':fields['Package'],'version':fields['Version'],'architecture':fields['Architecture']})
   if fields['Architecture']=='all':item['allow_arch_all']=True
   if record.get('build_root_only'):item['build_root_only']=True
  for tool in defaults['native_toolchain_inputs']:
   path=a.base/tool['receipt'];record=json.loads(path.read_text());assert sha(path)==tool['receipt_sha256']
   f=path.parent/tool['file'];assert sha(f)==record['package_sha256'];out.write(capture(['dpkg-deb','-f',f]).strip()+'\n\n')
 pool=list(grouped.values());(a.output/'build-pool-inputs.json').write_text(json.dumps(pool,indent=2)+'\n')
 (a.output/'build-pool-artifacts.json').write_text(json.dumps(artifacts,indent=2)+'\n')
 r['pool_artifacts_sha256']=sha(a.output/'build-pool-artifacts.json')
 sources=a.output/'Sources';count=0
 with sources.open('w') as out:
  for name in profile['packages']:
   settings={**profile,**profile.get('package_inputs',{}).get(name,{})}
   lock=json.loads((a.project/settings['source_lock']).read_text());component=lock['components'].get(name)
   if not component:r['missing_sources'].append(name);continue
   dsc=a.base/settings['source_cache']/component['dsc']
   if not dsc.exists():r['missing_sources'].append(name);continue
   expected=next(x['sha256'] for x in component['files'] if x['filename']==component['dsc']);assert sha(dsc)==expected
   source=Dsc(dsc.open());source['Package']=source.pop('Source')
   # Same genuine crossbuild-core packages required by our sbuild config.
   core='tabor-spe-toolchain:native (= 8.5.0+tabor5), binutils-powerpc-linux-gnu:native, libc6-dev:powerpcspe, linux-libc-dev:native (= '+defaults['uapi_version']+')'
   source['Build-Depends']=source.get('Build-Depends','')+(', ' if source.get('Build-Depends') else '')+core
   out.write(str(source)+'\n');count+=1
 cmd=['dose-builddebcheck','--deb-native-arch=amd64','--deb-host-arch=powerpcspe','--deb-profiles=cross,nocheck','--deb-drop-b-d-indep','--deb-emulate-sbuild','--failures','--successes','--explain',str(native),str(binaries),str(sources)]
 with (a.output/'dependency-report.yaml').open('w') as out,(a.output/'dose.log').open('w') as err:
  result=subprocess.run(cmd,stdout=out,stderr=err)
 assert result.returncode in [0,1], 'dose tool error; inspect dose.log'
 report=yaml.load((a.output/'dependency-report.yaml').read_text(),Loader=yaml.BaseLoader)
 (a.output/'dependency-report.json').write_text(json.dumps(report,indent=2)+'\n')
 r.update(status='debian-dependency-audit-completed',source_count=count,binary_package_names=len(artifact_names),dose_exit=result.returncode,command=cmd,report_sha256=sha(a.output/'dependency-report.yaml'),pool_inputs_sha256=sha(a.output/'build-pool-inputs.json'))
except BaseException as error:
 r.update(status='failed',error=str(error));raise
finally:(a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
