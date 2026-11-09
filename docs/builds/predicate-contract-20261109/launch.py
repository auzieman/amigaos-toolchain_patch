from pathlib import Path
import json,hashlib,subprocess
b=Path('/srv/data1/tabor-build/linux-live-001/work');p=b/'e2e-usb-20261108-010';w=b/'e2e-usb-20261109-011';inputs=Path('/home/owner/predicate-contract-20261109');inputs.mkdir(exist_ok=True);w.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((p/'receipt.json').read_text());assert r['status']=='complete-kernel-modules-firmware-bundle-not-installed'
for n in ['source','output']:subprocess.run(['cp','-a','--reflink=auto',str(p/n),str(w/n)],check=True)
patch=Path('/home/owner/predicate-contract-20261109/0031-ring-initialize-predicate-through-encoder.patch');rel='drivers/gpu/drm/amd/amdgpu/amdgpu_ring.c'
stage={'parent_candidate':p.name,'patch_sha256':sha(patch),'inputs':{rel:sha(w/'source'/rel)},'hardware_tested':False,'kind':'Initialize conditional predicate through existing scoped encoder'}
subprocess.run(['git','apply','--check',str(patch)],cwd=w/'source',check=True);subprocess.run(['git','apply',str(patch)],cwd=w/'source',check=True)
stage['outputs']={rel:sha(w/'source'/rel)};(w/'boundary-stage.json').write_text(json.dumps(stage,indent=2)+'\n')
s=Path('/home/owner/ib-envelope-20261108/build.py').read_text()
s=s.replace('e2e-usb-20261108-010','NEXT').replace('e2e-usb-20261108-009','e2e-usb-20261108-010').replace('NEXT','e2e-usb-20261109-011')
s=s.replace('tabor-e2e-010','NEXT').replace('tabor-e2e-009','tabor-e2e-010').replace('NEXT','tabor-e2e-011')
previous=json.loads((b/'e2e-usb-20261108-009/receipt.json').read_text())
s=s.replace(previous['module_verification']['module_sha256'],r['module_verification']['module_sha256'])
s=s.replace(previous['config_sha256'],r['config_sha256'])
(inputs/'build.py').write_text(s)
cmd=json.loads((p/'launch.json').read_text())['argv'];cmd=[x.replace('e2e-usb-20261108-010','e2e-usb-20261109-011').replace('tabor-e2e-usb-build-010','tabor-e2e-usb-build-011').replace('/home/owner/ib-envelope-20261108','/home/owner/predicate-contract-20261109') for x in cmd]
x=subprocess.run(cmd,capture_output=True,text=True);(w/'launch.json').write_text(json.dumps({'argv':cmd,'exit':x.returncode,'stdout':x.stdout,'stderr':x.stderr},indent=2)+'\n');x.check_returncode();print(x.stdout)
