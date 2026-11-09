from pathlib import Path
import json,subprocess,hashlib,difflib
b=Path('/srv/data1/tabor-build/linux-live-001/work');parent=b/'e2e-usb-20261109-012';w=b/'e2e-usb-20261109-013';inputs=Path('/home/owner/user-ib-fetch-20261109');inputs.mkdir(exist_ok=True);w.mkdir(exist_ok=False)
r=json.loads((parent/'receipt.json').read_text());assert r['status']=='complete-kernel-modules-firmware-bundle-not-installed'
for name in ['source','output']:subprocess.run(['cp','-a','--reflink=auto',str(parent/name),str(w/name)],check=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();base=w/'source/drivers/gpu/drm/amd/amdgpu';patch=[];before={};after={}
changes={
'amdgpu.h':('extern int amdgpu_vm_update_mode;','extern int amdgpu_vm_update_mode;\nextern bool amdgpu_polaris11_le_user_ib;'),
'amdgpu_drv.c':('int amdgpu_vm_update_mode = -1;','''int amdgpu_vm_update_mode = -1;
/* Diagnostic only: callers must explicitly submit LE GFX IB bytes. */
bool amdgpu_polaris11_le_user_ib;
module_param_named(polaris11_le_user_ib, amdgpu_polaris11_le_user_ib, bool, 0444);
MODULE_PARM_DESC(polaris11_le_user_ib, "Polaris11 BE diagnostic: fetch explicit LE userspace GFX IBs without legacy hardware swapping (default off)");'''),
'amdgpu_cs.c':('ib->flags = chunk_ib->flags;\n\treturn 0;','''ib->flags = chunk_ib->flags;
#ifdef __BIG_ENDIAN
	/* This option changes the fetch contract, not the command values. */
	if (amdgpu_polaris11_le_user_ib &&
	    p->adev->asic_type == CHIP_POLARIS11 &&
	    ring->funcs->type == AMDGPU_RING_TYPE_GFX)
		ib->is_le = true;
#endif
	return 0;''')}
for name,(old,new) in changes.items():
 p=base/name;s=p.read_text();assert s.count(old)==1;before['drivers/gpu/drm/amd/amdgpu/'+name]=sha(p);n=s.replace(old,new);p.write_text(n);after['drivers/gpu/drm/amd/amdgpu/'+name]=sha(p);patch+=list(difflib.unified_diff(s.splitlines(True),n.splitlines(True),fromfile='a/drivers/gpu/drm/amd/amdgpu/'+name,tofile='b/drivers/gpu/drm/amd/amdgpu/'+name))
p=inputs/'0033-polaris-user-ib-explicit-le-diagnostic.patch';p.write_text(''.join(patch));(w/'boundary-stage.json').write_text(json.dumps({'parent_candidate':parent.name,'patch_sha256':sha(p),'inputs':before,'outputs':after,'hardware_tested':False,'kind':'Default-off read-only scoped explicit-LE GFX user IB fetch diagnostic; no blanket serialization'},indent=2)+'\n')
s=Path('/home/owner/vm-pte-contract-20261109/build.py').read_text();s=s.replace('e2e-usb-20261109-012','NEXT').replace('e2e-usb-20261109-011','e2e-usb-20261109-012').replace('NEXT','e2e-usb-20261109-013');s=s.replace('tabor-e2e-012','NEXT').replace('tabor-e2e-011','tabor-e2e-012').replace('NEXT','tabor-e2e-013')
old=json.loads((b/'e2e-usb-20261109-011/receipt.json').read_text());s=s.replace(old['module_verification']['module_sha256'],r['module_verification']['module_sha256']).replace(old['config_sha256'],r['config_sha256']);(inputs/'build.py').write_text(s)
cmd=json.loads((parent/'launch.json').read_text())['argv'];cmd=[x.replace('e2e-usb-20261109-012','e2e-usb-20261109-013').replace('tabor-e2e-usb-build-012','tabor-e2e-usb-build-013').replace('/home/owner/vm-pte-contract-20261109','/home/owner/user-ib-fetch-20261109') for x in cmd]
r=subprocess.run(cmd,capture_output=True,text=True);(w/'launch.json').write_text(json.dumps({'argv':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n');print(r.stdout,r.stderr);r.check_returncode()
