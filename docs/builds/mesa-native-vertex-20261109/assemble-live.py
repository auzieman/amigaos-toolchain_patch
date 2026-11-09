from pathlib import Path
import shutil,hashlib,json,tarfile,subprocess
w=Path('/srv/data1/tabor-build/linux-live-001/work/native-vertex-contract-20261109-001')
d=Path('/home/owner/native-vertex-live-20261109-001');assert not d.exists();d.mkdir()
assert (w/'native-vertex-spe.exit').read_text().strip()=='0'
expected=json.loads((w/'native-vertex-regression.json').read_text())['candidate_libgallium_sha256']
assert hashlib.sha256((w/'offline-spe-output/usr/lib/libgallium-25.0.7.so').read_bytes()).hexdigest()==expected
root=d/'root';shutil.copytree('/home/owner/piglit-standard-live-20261109-001/root',root,symlinks=True)
for p in (w/'offline-spe-output/usr/lib').rglob('*'):
 if (p.is_file() or p.is_symlink()) and '.so' in p.name and 'shim' not in p.name:
  q=root/'usr/lib'/p.relative_to(w/'offline-spe-output/usr/lib');q.parent.mkdir(parents=True,exist_ok=True)
  if q.exists() or q.is_symlink():q.unlink()
  if p.is_symlink():
   assert not p.readlink().is_absolute();q.symlink_to(p.readlink())
  else:shutil.copy2(p,q)
assert not list(root.rglob('*shim*'))
assert not list(root.rglob('*stat-compat*'))
for name in ['dev','proc','sys','run','tmp']:
 p=root/name;assert not any(p.iterdir()),name
files={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file() and not p.is_symlink()}
links={str(p.relative_to(root)):str(p.readlink()) for p in root.rglob('*') if p.is_symlink()}
receipt={'candidate':str(w),'files':files,'symlinks':links,'libgallium_sha256':expected,'purpose':'stage only; no GPU access or rendering','hardware_render_tested':False,'option_default':'off','required_diagnostic_options':['TABOR_NATIVE_VERTEX_DATA=1','TABOR_POLARIS11_LE_IB=1','MESA_SHADER_CACHE_DISABLE=true'],'excluded':['no-op DRM shims','time64 shim adapter'],'interfaces_mounted':False}
(d/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
with tarfile.open(d/'runtime.tar','w') as t:
 for p in root.iterdir():t.add(p,arcname=p.name)
r=subprocess.run(['qemu-ppc','-cpu','e500v2','-L',str(root),str(root/'lib/ld.so.1'),'--library-path',str(root/'lib')+':'+str(root/'usr/lib'),'--list',str(root/'usr/bin/shader_runner_gles2')],capture_output=True,text=True,timeout=20)
(d/'loader-check.txt').write_text(r.stdout+r.stderr);assert r.returncode==0
print('Stage-only runtime assembled,',len(files),'regular files,',sum(p.stat().st_size for p in root.rglob('*') if p.is_file() and not p.is_symlink()),'bytes; loader dependency check passed; no shim or GPU execution')
