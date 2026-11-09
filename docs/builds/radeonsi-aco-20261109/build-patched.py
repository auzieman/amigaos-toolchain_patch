from pathlib import Path
import subprocess,json,hashlib
b=Path('/srv/data1/tabor-build/linux-live-001');parent=b/'work/radeonsi-aco-20261109-001';w=b/'work/radeonsi-aco-20261109-002';assert (parent/'status').read_text().strip()=='built-not-runtime-validated'
subprocess.run(['cp','-a','--reflink=auto',str(parent),str(w)],check=True)
inputs=Path('/home/owner/radeonsi-aco-boundary-20261109');check=json.loads((inputs/'check.json').read_text());assert check['status']=='PASS'
patch=inputs/'0001-radeonsi-serialize-aco-exec-after-relocation.patch';assert hashlib.sha256(patch.read_bytes()).hexdigest()==check['patch_sha256']
subprocess.run(['git','apply','--check',str(patch)],cwd=w/'mesa-source',check=True);subprocess.run(['git','apply',str(patch)],cwd=w/'mesa-source',check=True)
(w/'patch-receipt.json').write_text(json.dumps({'parent':str(parent),'patch_sha256':check['patch_sha256'],'scope':'ACO executable upload only after native relocation; other byte layouts unchanged','hardware_tested':False,'historical_container_path_alias':'/work/radeonsi-aco-20261109-001'},indent=2)+'\n')
# Existing Meson outputs retain their accepted logical /work path. The alias
# points only at this private copy, never at the baseline build.
cmd=['docker','run','-d','--name','tabor-radeonsi-aco-20261109-002','--cpus=2','--memory=4g','--network=none','-v',str(w)+':/work/radeonsi-aco-20261109-001','-v',str(b/'tools/cxx-reference-002')+':/tools:ro','-v',str(b/'sysroot')+':/sysroot:ro','--entrypoint','sh','sha256:0434a7f8dfeec379cd81d334e2a2eaa02208653e494d56334bcc486950be8a49','-c',
'''w=/work/radeonsi-aco-20261109-001
echo compiling-boundary-fix > "$w/status"
ninja -C "$w/build" -j2 > "$w/patch-build.log" 2>&1 || { echo compile-failed > "$w/status"; exit 1; }
DESTDIR="$w/output" ninja -C "$w/build" install > "$w/patch-install.log" 2>&1 || { echo install-failed > "$w/status"; exit 1; }
echo built-patched-not-runtime-validated > "$w/status"''']
r=subprocess.run(cmd,capture_output=True,text=True);(w/'launch-patched.json').write_text(json.dumps({'argv':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n');r.check_returncode();print(r.stdout)
