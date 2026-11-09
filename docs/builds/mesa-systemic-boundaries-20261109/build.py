from pathlib import Path
import subprocess,json,hashlib
b=Path('/srv/data1/tabor-build/linux-live-001');e=b/'work/mesa-systemic-boundaries-20261109-001';old=b/'work/radeonsi-le-ib-20261109-001';w=b/'work/radeonsi-systemic-20261109-001';assert not w.exists()
subprocess.run(['cp','-a','--reflink=auto',str(old),str(w)],check=True)
r=json.loads((e/'float-mode-check.json').read_text());patch=e/'0006-aco-float-mode-host-layout.patch';assert r['status']=='PASS';assert hashlib.sha256(patch.read_bytes()).hexdigest()==r['patch_sha256']
subprocess.run(['git','apply','--check',str(patch)],cwd=w/'mesa-source',check=True);subprocess.run(['git','apply',str(patch)],cwd=w/'mesa-source',check=True)
(e/'build-parent.json').write_text(json.dumps({'parent':str(old),'output':str(w),'patch_sha256':r['patch_sha256'],'host_layout_check':r,'hardware_tested':False},indent=2)+'\n')
argv=json.loads((w/'launch-le-ib.json').read_text())['argv'];argv=[x.replace('tabor-radeonsi-le-ib-fence-20261109-001','tabor-radeonsi-systemic-20261109-001').replace(str(old)+':',str(w)+':').replace('le-ib-build.log','systemic-build.log').replace('le-ib-install.log','systemic-install.log') for x in argv]
r=subprocess.run(argv,capture_output=True,text=True);(e/'launch.json').write_text(json.dumps({'argv':argv,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n');print(r.stdout,r.stderr);r.check_returncode()
