#!/usr/bin/env python3
"""R730 proof using mmdebstrap roots and standard Debian sbuild/unshare.

Only metadata/input retention surrounds sbuild; no custom dependency solver,
installed-state rewriting or manual target package installation is performed.
"""
import argparse,hashlib,json,os,pwd,re,shutil,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--project',type=Path,required=True)
p.add_argument('--base',type=Path,required=True)
p.add_argument('--spec',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();spec=json.loads(a.spec.read_text())
base_lock=json.loads((a.project/spec['base_lock']).read_text())
assert spec['uapi_version']==base_lock['target_foundation']['linux_uapi_local'], 'UAPI version differs from frozen base'
assert a.output.resolve().is_relative_to((a.base/'work').resolve())
a.output.mkdir(exist_ok=False)
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
r={'status':'preparing','spec_sha256':sha(a.spec),'recipe_sha256':sha(Path(__file__)),
   'method':'Debian mmdebstrap buildd root and sbuild unshare apt resolver',
   'build_architecture':'amd64','host_architecture':spec.get('host_architecture','powerpcspe'),
   'target_execution':False,'target_installation':False,'boot_image_ready':False,
   'build_root_only':bool(spec.get('build_root_only')),'bootstrap_assembly':bool(spec.get('bootstrap_assembly')),
   'source_inputs':[],'extra_package_inputs':[],'commands':[], 'package':spec['package']}
def save():(a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
def run(cmd,name,env=None,cwd=None):
 r['commands'].append(list(map(str,cmd)));save()
 with (a.output/(name+'.log')).open('w') as log:
  return subprocess.run(list(map(str,cmd)),stdout=log,stderr=subprocess.STDOUT,env=env,cwd=cwd).returncode
try:
 lock=json.loads((a.project/spec['source_lock']).read_text())
 component=lock['components'][spec['package']]
 if spec['package'] in ['linux','glibc']:
  assert component['version']==base_lock['target_foundation'][spec['package']], 'Foundation source version differs from frozen base'
 r['source_version']=component['version'];sources=a.output/'sources';sources.mkdir()
 for entry in component['files']:
  assert Path(entry['filename']).name==entry['filename']
  src=a.base/spec['source_cache']/entry['filename'];assert sha(src)==entry['sha256']
  shutil.copyfile(src,sources/src.name);r['source_inputs'].append(entry)
 extras=a.output/'extra-packages';extras.mkdir()
 for item in spec['extra_receipts']:
  receipt=a.base/item['receipt'];assert receipt.resolve().is_relative_to(a.base.resolve())
  assert sha(receipt)==item['sha256']
  record=json.loads(receipt.read_text());assert record['status']=='debian-packages-built-not-target-installed'
  assert bool(record.get('build_root_only'))==bool(item.get('build_root_only')), 'Bootstrap-only input requires explicit role'
  if record.get('build_root_only'):
   assert set(item['packages']) <= {'tabor-spe-libgcc-s1','tabor-spe-libstdc++6','tabor-spe-libatomic1'}
  found=set()
  for name,entry in record['packages'].items():
   if not name.endswith('.deb') or (item.get('files') and name not in item['files']):continue
   assert Path(name).name==name
   package=name.split('_',1)[0]
   if package not in item['packages']:continue
   src=receipt.parent/name;assert sha(src)==entry['sha256']
   assert subprocess.check_output(['dpkg-deb','-f',str(src),'Package'],text=True).strip()==package
   arch=subprocess.check_output(['dpkg-deb','-f',str(src),'Architecture'],text=True).strip()
   assert arch=='powerpcspe' or (arch=='all' and item.get('allow_arch_all'))
   assert not (extras/name).exists();shutil.copyfile(src,extras/name)
   found.add(package)
   r['extra_package_inputs'].append({'file':name,'sha256':entry['sha256'],'receipt_sha256':sha(receipt)})
  assert set(item['packages'])==found, 'Requested packages absent from the pinned receipt'
 for item in spec.get('native_toolchain_inputs',[]):
  receipt=a.base/item['receipt'];assert sha(receipt)==item['receipt_sha256']
  record=json.loads(receipt.read_text());assert record['status']=='native-toolchain-package-built-not-installed'
  src=receipt.parent/item['file'];assert sha(src)==record['package_sha256']
  assert subprocess.check_output(['dpkg-deb','-f',str(src),'Package'],text=True).strip()=='tabor-spe-toolchain'
  assert subprocess.check_output(['dpkg-deb','-f',str(src),'Architecture'],text=True).strip()=='amd64'
  shutil.copyfile(src,extras/src.name)
  r['extra_package_inputs'].append({'file':src.name,'sha256':sha(src),'role':'native SPE cross compiler','receipt_sha256':sha(receipt)})
 root_receipt=a.base/spec['native_root_receipt'];assert sha(root_receipt)==spec['native_root_receipt_sha256']
 root_record=json.loads(root_receipt.read_text());assert root_record['status']=='native-buildd-root-created'
 assert root_record.get('base_lock_sha256')==sha(a.project/spec['base_lock']), 'Root must match the frozen base lock'
 root_tar=root_receipt.parent/'trixie-amd64.tar';assert sha(root_tar)==root_record['sha256']
 r['native_root_receipt_sha256']=sha(root_receipt);r['native_root_sha256']=sha(root_tar)
 dsc=sources/component['dsc']
 if spec.get('quilt_patch_series'):
  series_spec=spec['quilt_patch_series'];series_path=a.project/series_spec['path']
  assert sha(series_path)==series_spec['sha256']
  series=json.loads(series_path.read_text());assert series['version']==component['version']
  tree=sources/'quilt-source'
  assert run(['dpkg-source','--no-check','-x',dsc,tree],'source-extract')==0
  assert (tree/'debian/source/format').read_text().strip()=='3.0 (quilt)'
  patchdir=tree/'debian/patches';patchdir.mkdir(exist_ok=True)
  quilt_series=patchdir/'series';previous=quilt_series.read_text() if quilt_series.exists() else ''
  for index,item in enumerate(series['patches']):
   patch=a.project/item['path'];assert sha(patch)==item['sha256']
   assert run(['git','-C',tree,'apply','--check',patch],'quilt-patch-check-'+str(index))==0
   name='tabor-'+patch.name;assert not (patchdir/name).exists()
   shutil.copyfile(patch,patchdir/name);previous=previous.rstrip()+'\n'+name+'\n';quilt_series.write_text(previous.lstrip())
   assert run(['quilt','push'],'quilt-patch-apply-'+str(index),env={**os.environ,'QUILT_PATCHES':'debian/patches','QUILT_PATCH_OPTS':'--fuzz=0'},cwd=tree)==0
  patched=sources/'patched-output';patched.mkdir()
  for entry in component['files']:
   if '.orig.tar.' in entry['filename']:os.link(sources/entry['filename'],patched/entry['filename'])
  assert run(['dpkg-source','-b',tree],'source-package',env={**os.environ,'XZ_OPT':'-T1'},cwd=patched)==0
  dsc=patched/component['dsc'];assert dsc.exists()
  r['patched_source']={'dsc':str(dsc.relative_to(a.output)),'sha256':sha(dsc),'version':component['version'],'quilt_series':series_spec,'patches':series['patches'],'preserve_debian_version':True}
 if spec.get('source_patch'):
  patch_spec=spec['source_patch'];patch=a.project/patch_spec['path'];assert sha(patch)==patch_spec['sha256']
  tree=sources/'patched-source'
  assert run(['dpkg-source','--no-check','-x',dsc,tree],'source-extract')==0
  assert run(['git','-C',tree,'apply','--check',patch],'source-patch-check')==0
  assert run(['git','-C',tree,'apply',patch],'source-patch')==0
  version=patch_spec['version']
  assert version.startswith(component['version']+'+')
  changelog=tree/'debian/changelog'
  entry=(spec['package']+' ('+version+') UNRELEASED; urgency=medium\n\n'
         '  * Register the SPE userspace UAPI include tuple in normal Debian export.\n\n'
         ' -- Tabor lab <root@localhost>  Mon, 02 Nov 2026 22:00:00 +0000\n\n')
  changelog.write_text(entry+changelog.read_text())
  if patch_spec.get('prepare_debian_control'):
   # Debian Linux explicitly requires control regeneration before automated
   # builds. Its control-real target intentionally returns 1 after success.
   result=run(['make','-f','debian/rules','debian/control'],'source-control-generation',env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},cwd=tree)
   if result:
    message=(a.output/'source-control-generation.log').read_text()
    assert result==2 and 'been generated SUCCESSFULLY.' in message, 'Control generation failed'
   assert run(['make','-f','debian/rules','debian/control'],'source-control-validation',env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},cwd=tree)==0
  assert run(['dpkg-source','-b',tree],'source-package',{**os.environ,'XZ_OPT':'-T1'},cwd=sources)==0
  candidates=[x for x in sources.glob('*.dsc') if x.name!=component['dsc']]
  assert len(candidates)==1;dsc=candidates[0]
  r['upstream_debian_source_version']=component['version'];r['source_version']=version
  r['patched_source']={'dsc':dsc.name,'sha256':sha(dsc),'patch_sha256':sha(patch),'version':version}
 config=a.output/'sbuild.conf'
 # Large dependency templates must unpack on server storage, not /tmp tmpfs:
 # tmpfs pages count against the package job's memory limit before compilation.
 # Keep this outside the private 0750 project parent: the mapped namespace
 # uid must traverse the temporary path without opening up private sources.
 build_tmp=a.base.parent.parent/'tabor-sbuild-tmp'
 build_tmp.mkdir(exist_ok=True)
 assert not build_tmp.is_symlink() and build_tmp.resolve().is_relative_to(a.base.parent.parent.resolve())
 assert build_tmp.stat().st_dev==a.base.stat().st_dev, 'Build temp must use the data filesystem'
 build_tmp.chmod(0o1777)
 uapi_version=spec['uapi_version']
 assert re.fullmatch(r'[0-9A-Za-z.+:~_-]+',uapi_version)
 core_version=spec.get('cross_core_version','1.0+spe2')
 assert core_version in ['1.0+spe2','1.0+spe3']
 config.write_text("$crossbuild_core_depends = { powerpcspe => ['crossbuild-essential-powerpcspe:native (= "+core_version+")'] };\n1;\n")
 with config.open('a') as f:
  f.write("$unshare_tmpdir_template = '"+str(build_tmp)+"/tmp.sbuild.XXXXXXXXXX';\n1;\n")
 if spec.get('configure_cache'):
  cache_spec=spec['configure_cache'];cache_path=a.project/cache_spec['path']
  assert sha(cache_path)==cache_spec['sha256']
  measured=json.loads(cache_path.read_text());values=measured['values']
  assert set(values)=={'xorg_cv_malloc0_returns_null'} and values['xorg_cv_malloc0_returns_null'] in ['yes','no']
  for evidence in cache_spec['evidence']:
   assert sha(a.project/evidence['path'])==evidence['sha256']
  r['configure_cache']=cache_spec;r['configure_cache_values']=values
  with config.open('a') as f:
   f.write("$build_environment = { 'xorg_cv_malloc0_returns_null' => '"+values['xorg_cv_malloc0_returns_null']+"' };\n1;\n")
 owner=pwd.getpwnam('owner');os.chown(a.output,owner.pw_uid,owner.pw_gid)
 # CROSSBUILD_CORE_DEPENDS is a documented sbuild per-port extension. Every
 # entry names a real installed/package-managed tool or target development pkg.
 # --nolog also prevents sbuild mail; stdout is retained locally instead.
 cmd=['runuser','-u','owner','--','env','SBUILD_CONFIG='+str(config),
      'DEB_BUILD_OPTIONS=nocheck parallel=4','sbuild','--chroot-mode=unshare','--chroot='+str(root_tar),
      '--build=amd64','--host='+spec.get('host_architecture','powerpcspe'),'--dist=trixie',
      '--profiles='+spec.get('build_profiles','cross,nocheck'),
      '--build-dep-resolver=apt','--no-run-lintian','--nolog','--jobs=4',
      '--build-dir='+str(a.output),str(dsc)]
 if spec.get('indep_only'):cmd[-1:-1]=['--arch-all','--no-arch-any']
 else:cmd[-1:-1]=['--no-arch-all']
 if list(extras.glob('*.deb')):cmd[-1:-1]=['--extra-package='+str(extras)]
 r['status']='sbuild-running';save()
 result=run(cmd,'sbuild',os.environ.copy())
 r['sbuild_exit']=result
 if result:raise RuntimeError('sbuild failed; retained standard dependency/build log')
 packages={f.name:{'sha256':sha(f),'bytes':f.stat().st_size} for f in a.output.glob('*.deb')}
 assert packages,'sbuild returned success without binary artifacts'
 r.update(status='debian-packages-built-not-target-installed',packages=packages)
 r['build_metadata']={f.name:sha(f) for pattern in ['*.buildinfo','*.changes'] for f in a.output.glob(pattern)}
 save()
 assert run(['python3',a.project/'scripts/inspect-spe-package-payloads.py','--receipt',a.output/'receipt.json',
             '--output',a.output/'payload-inspection.json'],'payload-inspection')==0
 r['payload_inspection_sha256']=sha(a.output/'payload-inspection.json')
except Exception as error:
 r.update(status='failed',error=str(error));raise
finally:save()
