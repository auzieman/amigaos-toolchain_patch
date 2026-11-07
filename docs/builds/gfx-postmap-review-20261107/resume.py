import json,hashlib,subprocess
from pathlib import Path
w=Path('/candidate');out=w/'output';module=out/'drivers/gpu/drm/amd/amdgpu/amdgpu.ko'
cmd=['make','-C',str(w/'source'),'O='+str(out),'ARCH=powerpc','CROSS_COMPILE=powerpc-linux-gnu-','-j4','drivers/gpu/drm/amd/amdgpu/amdgpu.ko']
r={'status':'started','command':cmd,'hardware_tested':False,'installed':False}
with (w/'build-002.log').open('w') as f:
 p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT);r['exit']=p.returncode
 if p.returncode==0:
  r['status']='compiled-not-installed';r['module_sha256']=hashlib.sha256(module.read_bytes()).hexdigest()
  subprocess.run(['powerpc-linux-gnu-readelf','-h',str(module)],stdout=f,stderr=subprocess.STDOUT,check=True)
  subprocess.run(['powerpc-linux-gnu-readelf','-p','.modinfo',str(module)],stdout=f,stderr=subprocess.STDOUT,check=True)
 else:r['status']='failed'
(w/'build-002.json').write_text(json.dumps(r,indent=2)+'\n')
raise SystemExit(r['exit'])
