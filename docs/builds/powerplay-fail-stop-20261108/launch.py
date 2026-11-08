
from pathlib import Path
import subprocess,json,hashlib
parent=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-004');w=parent.with_name('e2e-usb-20261108-005');inputs=Path('/home/owner/powerplay-fail-stop-20261108');inputs.mkdir(exist_ok=True)
assert not w.exists()
r=json.loads((parent/'receipt.json').read_text());assert r['status']=='complete-kernel-modules-firmware-bundle-not-installed'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert int(Path('/proc/meminfo').read_text().split('MemAvailable:')[1].split()[0])>8*1024*1024
assert not subprocess.check_output(['docker','ps','--filter','name=tabor-e2e-usb-build','-q'],text=True).strip()
w.mkdir()
for name in ['source','output']:subprocess.run(['cp','-a','--reflink=auto',str(parent/name),str(w/name)],check=True)
patch=Path('/srv/data1/tabor-build/source-review/powerplay-fail-stop-20261108/0025-smu7-stop-state-transition-on-error.patch');rel='drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_hwmgr.c'
stage={'parent_candidate':parent.name,'patch_sha256':sha(patch),'inputs':{rel:sha(w/'source'/rel)},'hardware_tested':False}
subprocess.run(['git','apply','--check',str(patch)],cwd=w/'source',check=True);subprocess.run(['git','apply',str(patch)],cwd=w/'source',check=True)
stage['outputs']={rel:sha(w/'source'/rel)};(w/'boundary-stage.json').write_text(json.dumps(stage,indent=2)+'\n');(inputs/'prepare.json').write_text(json.dumps(stage,indent=2)+'\n')
build=Path('/home/owner/state-clock-decode-20261108/build.py').read_text()
build=build.replace('e2e-usb-20261108-004','NEWCANDIDATE').replace('e2e-usb-20261108-003','e2e-usb-20261108-004').replace('NEWCANDIDATE','e2e-usb-20261108-005')
build=build.replace('tabor-e2e-004','NEWRELEASE').replace('tabor-e2e-003','tabor-e2e-004').replace('NEWRELEASE','tabor-e2e-005')
build=build.replace('48799ed982a9e52f189d22e8f9d142fcc1db048ecacc35fba6c69eb7a8b42f16',r['module_verification']['module_sha256']).replace('5153c1351657962f99fe69ba9a75376dfa1f73f9f2a1d85a82c89e948d1d88ea',sha(parent/'output/.config'))
(inputs/'build.py').write_text(build)
launch=json.loads((parent/'launch.json').read_text())['argv']
launch=[a.replace('e2e-usb-20261108-004','e2e-usb-20261108-005').replace('tabor-e2e-usb-build-004','tabor-e2e-usb-build-005').replace('src=/home/owner/state-clock-decode-20261108,dst=/inputs','src=/home/owner/powerplay-fail-stop-20261108,dst=/inputs') for a in launch]
p=subprocess.run(launch,capture_output=True,text=True);(w/'launch.json').write_text(json.dumps({'argv':launch,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr},indent=2)+'\n');print(p.stdout,p.stderr);p.check_returncode()
