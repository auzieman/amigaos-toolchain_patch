from pathlib import Path
import subprocess,json,hashlib
parent=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-002')
w=parent.with_name('e2e-usb-20261108-003')
inputs=Path('/home/owner/uvd-encoder-codec-20261108')
assert not w.exists()
assert json.loads((parent/'receipt.json').read_text())['status']=='complete-kernel-modules-firmware-bundle-not-installed'
assert int(Path('/proc/meminfo').read_text().split('MemAvailable:')[1].split()[0])>8*1024*1024
w.mkdir()
for name in ['source','output']:subprocess.run(['cp','-a','--reflink=auto',str(parent/name),str(w/name)],check=True)
stage=json.loads((inputs/'prepare.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
patch=inputs/'0023-polaris11-uvd-encoder-shared-le.patch'
assert sha(patch)==stage['patch_sha256']
for name,h in stage['inputs'].items():assert sha(w/'source'/name)==h
subprocess.run(['git','apply','--check',str(patch)],cwd=w/'source',check=True)
subprocess.run(['git','apply',str(patch)],cwd=w/'source',check=True)
for name,h in stage['outputs'].items():assert sha(w/'source'/name)==h
(w/'boundary-stage.json').write_text(json.dumps(stage,indent=2)+'\n')
launch=json.loads((inputs/'launch-parent.json').read_text())['argv']
launch=[a.replace('e2e-usb-20261108-002','e2e-usb-20261108-003').replace('tabor-e2e-usb-build-002','tabor-e2e-usb-build-003').replace('src=/home/owner/shared-boundary-20261108,dst=/inputs','src=/home/owner/uvd-encoder-codec-20261108,dst=/inputs') for a in launch]
r=subprocess.run(launch,capture_output=True,text=True)
(w/'launch.json').write_text(json.dumps({'argv':launch,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n')
print(r.stdout,r.stderr);r.check_returncode()
