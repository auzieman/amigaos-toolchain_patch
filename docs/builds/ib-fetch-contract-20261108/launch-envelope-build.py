from pathlib import Path
import json,hashlib,subprocess
b=Path('/srv/data1/tabor-build/linux-live-001/work');p=b/'e2e-usb-20261108-009';w=b/'e2e-usb-20261108-010';inputs=Path('/home/owner/ib-envelope-20261108');inputs.mkdir(exist_ok=True);w.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((p/'receipt.json').read_text());assert r['status']=='complete-kernel-modules-firmware-bundle-not-installed'
for n in ['source','output']:subprocess.run(['cp','-a','--reflink=auto',str(p/n),str(w/n)],check=True)
patch=Path('/home/owner/ib-fetch-contract-20261108/0030-gfx8-cpu-envelope-snapshot.patch');rel='drivers/gpu/drm/amd/amdgpu/gfx_v8_0.c'
stage={'parent_candidate':p.name,'patch_sha256':sha(patch),'inputs':{rel:sha(w/'source'/rel)},'hardware_tested':False,'kind':'CPU-only timeout snapshot; no extra GPU commands'}
subprocess.run(['git','apply','--check',str(patch)],cwd=w/'source',check=True);subprocess.run(['git','apply',str(patch)],cwd=w/'source',check=True)
stage['outputs']={rel:sha(w/'source'/rel)};(w/'boundary-stage.json').write_text(json.dumps(stage,indent=2)+'\n')
s=Path('/home/owner/ib-fetch-contract-20261108/build.py').read_text()
s=s.replace('e2e-usb-20261108-009','NEXT').replace('e2e-usb-20261108-008','e2e-usb-20261108-009').replace('NEXT','e2e-usb-20261108-010')
s=s.replace('tabor-e2e-009','NEXT').replace('tabor-e2e-008','tabor-e2e-009').replace('NEXT','tabor-e2e-010')
s=s.replace('6fd480b5ca4c0bbd22c1aa98d0cbed4d2fb52373d474918d033f9ff9efcae4f4',r['module_verification']['module_sha256'])
s=s.replace('6034a61a6cb2055c5f4abd55aad1f0c209a76c333a9b47cc8380147d28c59cea',r['config_sha256'])
s=s.replace('03001919041721081205','03007431041721021451').replace('a1221105-02','a1221108-02')
(inputs/'build.py').write_text(s)
cmd=json.loads((p/'launch.json').read_text())['argv'];cmd=[x.replace('e2e-usb-20261108-009','e2e-usb-20261108-010').replace('tabor-e2e-usb-build-009','tabor-e2e-usb-build-010').replace('/home/owner/ib-fetch-contract-20261108','/home/owner/ib-envelope-20261108') for x in cmd]
x=subprocess.run(cmd,capture_output=True,text=True);(w/'launch.json').write_text(json.dumps({'argv':cmd,'exit':x.returncode,'stdout':x.stdout,'stderr':x.stderr},indent=2)+'\n');x.check_returncode();print(x.stdout)
