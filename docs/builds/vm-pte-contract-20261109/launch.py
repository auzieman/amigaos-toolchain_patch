from pathlib import Path
import subprocess,json,hashlib
b=Path('/srv/data1/tabor-build/linux-live-001/work');parent=b/'e2e-usb-20261109-011';w=b/'e2e-usb-20261109-012';inputs=Path('/home/owner/vm-pte-contract-20261109')
check=json.loads((inputs/'check.json').read_text());assert check['status']=='PASS';r=json.loads((parent/'receipt.json').read_text());assert r['status']=='complete-kernel-modules-firmware-bundle-not-installed';w.mkdir(exist_ok=False)
for name in ['source','output']:subprocess.run(['cp','-a','--reflink=auto',str(parent/name),str(w/name)],check=True)
p=inputs/'0032-vm-sdma-serialize-copied-pte-array.patch';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(p)==check['patch_sha256'];rel='drivers/gpu/drm/amd/amdgpu/amdgpu_vm_sdma.c';assert sha(w/'source'/rel)==check['source_sha256']
subprocess.run(['git','apply','--check',str(p)],cwd=w/'source',check=True);subprocess.run(['git','apply',str(p)],cwd=w/'source',check=True)
(w/'boundary-stage.json').write_text(json.dumps({'parent_candidate':parent.name,'patch_sha256':sha(p),'inputs':{rel:check['source_sha256']},'outputs':{rel:sha(w/'source'/rel)},'hardware_tested':False,'kind':'GPU-visible PTE array LE serialization before raw SDMA copy'},indent=2)+'\n')
s=Path('/home/owner/predicate-contract-20261109/build.py').read_text()
s=s.replace('e2e-usb-20261109-011','e2e-usb-20261109-012').replace('e2e-usb-20261108-010','e2e-usb-20261109-011')
s=s.replace('tabor-e2e-011','NEXT').replace('tabor-e2e-010','tabor-e2e-011').replace('NEXT','tabor-e2e-012')
s=s.replace('952e27395154f230a5903a40b7204d301032825ab3ee934c266cbcaf8baccc3b',r['module_verification']['module_sha256']).replace('e93213384c3d6cea34093a336768aecb9ea34bdb0d889a60d36cd1cdca27617f',r['config_sha256'])
(inputs/'build.py').write_text(s)
cmd=json.loads((parent/'launch.json').read_text())['argv'];cmd=[x.replace('e2e-usb-20261109-011','e2e-usb-20261109-012').replace('tabor-e2e-usb-build-011','tabor-e2e-usb-build-012').replace('/home/owner/predicate-contract-20261109','/home/owner/vm-pte-contract-20261109') for x in cmd]
r=subprocess.run(cmd,capture_output=True,text=True);(w/'launch.json').write_text(json.dumps({'argv':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n');print(r.stdout,r.stderr);r.check_returncode()
