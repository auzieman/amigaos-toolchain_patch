from pathlib import Path
import runpy,tempfile,hashlib,json,shutil,subprocess
b=Path('/srv/data1/tabor-build/linux-live-001');w=b/'work/gfx-postmap-review-20261107-001';ref=b/'work/gfx-map-stage-20261107-001'
inspect=runpy.run_path('/home/owner/gfx-postmap-review-20261108/verify-ppc32-module.py')['inspect']
module=w/'output-matched/drivers/gpu/drm/amd/amdgpu/amdgpu.ko';symvers=ref/'output/Module.symvers'
result={'negative_controls':{},'source_replay':{}}
try:inspect(module,'7.3.0-rc6-tabor-upstream-001',symvers)
except ValueError as e:result['negative_controls']['wrong_release']=str(e)
else:raise AssertionError('wrong release accepted')
with tempfile.TemporaryDirectory(prefix='gpu-review-controls-',dir='/home/owner') as tmp:
 temp=Path(tmp);lines=symvers.read_text().splitlines();modified=False
 for i,line in enumerate(lines):
  fields=line.split()
  if fields[1]=='module_layout':fields[0]='0x%08x'%(int(fields[0],16)^1);lines[i]='\t'.join(fields);modified=True
 assert modified;bad=temp/'negative-only.symvers';bad.write_text('\n'.join(lines)+'\n')
 try:inspect(module,'6.12.113-tabor-modular',bad)
 except ValueError as e:result['negative_controls']['wrong_module_layout_crc']=str(e)
 else:raise AssertionError('wrong ABI accepted')
 for path in ['drivers/gpu/drm/amd/amdgpu/gfx_v8_0.c','drivers/gpu/drm/amd/amdgpu/amdgpu_ring.c','drivers/gpu/drm/amd/amdgpu/amdgpu_device.c']:
  p=temp/path;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ref/'source'/path,p)
 for name in ['0014-gfx8-upstream-ring-test-corrections.patch','0015-polaris-postmap-initialization-boundaries.patch']:
  p=Path('/home/owner/gfx-postmap-review-20261107')/name
  subprocess.run(['git','apply','--check',str(p)],cwd=temp,check=True)
  subprocess.run(['git','apply',str(p)],cwd=temp,check=True)
 for path in ['drivers/gpu/drm/amd/amdgpu/gfx_v8_0.c','drivers/gpu/drm/amd/amdgpu/amdgpu_ring.c','drivers/gpu/drm/amd/amdgpu/amdgpu_device.c']:
  a=(temp/path).read_bytes();z=(w/'source'/path).read_bytes();assert a==z,path;result['source_replay'][path]=hashlib.sha256(a).hexdigest()
print(json.dumps(result,indent=2))
