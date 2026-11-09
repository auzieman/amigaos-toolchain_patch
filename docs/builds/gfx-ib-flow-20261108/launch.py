from pathlib import Path
import hashlib,json,subprocess
base=Path('/srv/data1/tabor-build/linux-live-001')
parent=base/'work/e2e-usb-20261108-007'
w=base/'work/e2e-usb-20261108-008'
inputs=Path('/home/owner/gfx-ib-flow-20261108')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((parent/'receipt.json').read_text())
assert r['status']=='complete-kernel-modules-firmware-bundle-not-installed'
assert r['module_verification']['module_sha256']=='9ae383a86f58807657ec6965c71021fa6b6c4c4de34bf09438e3a68361f6f475'
assert json.loads((inputs/'receipt.json').read_text())['status']=='PASS'
assert not subprocess.check_output(['docker','ps','--filter','name=tabor-e2e-usb-build','-q'],text=True).strip()
w.mkdir(exist_ok=False)
for name in ['source','output']:subprocess.run(['cp','-a','--reflink=auto',str(parent/name),str(w/name)],check=True)
patch=inputs/'0028-gfx8-decode-ib-test-writeback-and-record-completion.patch'
rel='drivers/gpu/drm/amd/amdgpu/gfx_v8_0.c'
stage={'parent_candidate':parent.name,'patch_sha256':sha(patch),'inputs':{rel:sha(w/'source'/rel)},'hardware_tested':False}
subprocess.run(['git','apply','--check',str(patch)],cwd=w/'source',check=True)
subprocess.run(['git','apply',str(patch)],cwd=w/'source',check=True)
stage['outputs']={rel:sha(w/'source'/rel)}
(w/'boundary-stage.json').write_text(json.dumps(stage,indent=2)+'\n')
build=Path('/home/owner/console-selected-path-20261108/build.py').read_text()
build=build.replace('e2e-usb-20261108-007','NEXT').replace('e2e-usb-20261108-006','e2e-usb-20261108-007').replace('NEXT','e2e-usb-20261108-008')
build=build.replace('tabor-e2e-007','NEXT').replace('tabor-e2e-006','tabor-e2e-007').replace('NEXT','tabor-e2e-008')
build=build.replace('39cb3f14c248af27a10ac04d970308c669f18b710deb7633c4380cab130a7a90',r['module_verification']['module_sha256'])
build=build.replace('af8ff9c065e883f3f54b23a4838e09f81f723db245d18b3968e934fa1602a5a4',sha(parent/'output/.config'))
build=build.replace("'-j4'","'-j2'")
(inputs/'build.py').write_text(build)
cmd=json.loads((parent/'launch.json').read_text())['argv']
cmd=[a.replace('e2e-usb-20261108-007','e2e-usb-20261108-008').replace('tabor-e2e-usb-build-007','tabor-e2e-usb-build-008').replace('/home/owner/console-selected-path-20261108','/home/owner/gfx-ib-flow-20261108').replace('--cpus=4','--cpus=2').replace('--memory=6g','--memory=4g') for a in cmd]
p=subprocess.run(cmd,capture_output=True,text=True)
(w/'launch.json').write_text(json.dumps({'argv':cmd,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr},indent=2)+'\n')
print(p.stdout,p.stderr);p.check_returncode()
