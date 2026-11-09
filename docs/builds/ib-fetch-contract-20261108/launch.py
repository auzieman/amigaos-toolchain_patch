from pathlib import Path
import hashlib,json,subprocess
base=Path('/srv/data1/tabor-build/linux-live-001');parent=base/'work/e2e-usb-20261108-008';w=base/'work/e2e-usb-20261108-009';inputs=Path('/home/owner/ib-fetch-contract-20261108')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((parent/'receipt.json').read_text());assert r['status']=='complete-kernel-modules-firmware-bundle-not-installed'
assert r['module_verification']['module_sha256']=='6fd480b5ca4c0bbd22c1aa98d0cbed4d2fb52373d474918d033f9ff9efcae4f4'
assert json.loads((inputs/'check.json').read_text())['status']=='PASS'
assert not subprocess.check_output(['docker','ps','--filter','name=tabor-e2e-usb-build','-q'],text=True).strip()
w.mkdir(exist_ok=False)
for name in ['source','output']:subprocess.run(['cp','-a','--reflink=auto',str(parent/name),str(w/name)],check=True)
patch=inputs/'0029-gfx8-test-explicit-little-endian-ib-fetch.patch';prep=json.loads((inputs/'prepare.json').read_text());prefix='drivers/gpu/drm/amd/amdgpu/'
stage={'parent_candidate':parent.name,'patch_sha256':sha(patch),'inputs':{prefix+n:h for n,h in prep['inputs'].items()},'hardware_tested':False}
for rel,h in stage['inputs'].items():assert sha(w/'source'/rel)==h
subprocess.run(['git','apply','--check',str(patch)],cwd=w/'source',check=True);subprocess.run(['git','apply',str(patch)],cwd=w/'source',check=True)
stage['outputs']={prefix+n:h for n,h in prep['outputs'].items()}
for rel,h in stage['outputs'].items():assert sha(w/'source'/rel)==h
(w/'boundary-stage.json').write_text(json.dumps(stage,indent=2)+'\n')
build=Path('/home/owner/gfx-ib-flow-20261108/build.py').read_text()
build=build.replace('e2e-usb-20261108-008','NEXT').replace('e2e-usb-20261108-007','e2e-usb-20261108-008').replace('NEXT','e2e-usb-20261108-009')
build=build.replace('tabor-e2e-008','NEXT').replace('tabor-e2e-007','tabor-e2e-008').replace('NEXT','tabor-e2e-009')
build=build.replace('9ae383a86f58807657ec6965c71021fa6b6c4c4de34bf09438e3a68361f6f475',r['module_verification']['module_sha256'])
build=build.replace(sha(parent.with_name('e2e-usb-20261108-007')/'output/.config'),sha(parent/'output/.config'))
(inputs/'build.py').write_text(build)
cmd=json.loads((parent/'launch.json').read_text())['argv']
cmd=[a.replace('e2e-usb-20261108-008','e2e-usb-20261108-009').replace('tabor-e2e-usb-build-008','tabor-e2e-usb-build-009').replace('/home/owner/gfx-ib-flow-20261108','/home/owner/ib-fetch-contract-20261108') for a in cmd]
p=subprocess.run(cmd,capture_output=True,text=True);(w/'launch.json').write_text(json.dumps({'argv':cmd,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr},indent=2)+'\n');print(p.stdout,p.stderr);p.check_returncode()
