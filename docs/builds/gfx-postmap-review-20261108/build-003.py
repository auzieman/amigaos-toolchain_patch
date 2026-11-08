import json,hashlib,subprocess,runpy
from pathlib import Path
w=Path('/candidate');ref=Path('/base/work/gfx-map-stage-20261107-001/output');src=Path('/base/work/tabor-smu-diagnostics-20261105-003/source');out=Path('/base/work/tabor-smu-diagnostics-20261105-003/output')
r={'status':'started','hardware_tested':False,'installed':False,'build_context':'private copy of complete accepted Kbuild output; fresh re-patched source'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
inspect=runpy.run_path('/inputs/verify-ppc32-module.py')['inspect']
try:
 assert sha(out/'.config')=='7effb33413cbb4ab6dcda93563c2600f1948f9764387df70cd016883892fdaec'
 assert sha(Path('/inputs/installed-reference-amdgpu.ko'))=='6c51a545081a6bb1b0f55641f1a3f14fbe6e7991362d4b3eb192b05b17c4404e'
 # Installed baseline acts as positive control against the accepted export table.
 r['reference_control']=inspect('/inputs/installed-reference-amdgpu.ko','6.12.113-tabor-modular',ref/'Module.symvers')
 cmd=['make','-C',str(src),'O='+str(out),'ARCH=powerpc','CROSS_COMPILE=powerpc-linux-gnu-','-j4','modules']
 r['command']=cmd
 with (w/'build-003.log').open('w') as f:
  proc=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT);r['exit']=proc.returncode
  if proc.returncode:raise RuntimeError('Kbuild modules failed')
 module=out/'drivers/gpu/drm/amd/amdgpu/amdgpu.ko'
 r['verification']=inspect(module,'6.12.113-tabor-modular',ref/'Module.symvers','/inputs/installed-reference-amdgpu.ko')
 r['config_sha256']=sha(out/'.config')
 r['status']='compiled-and-export-crcs-verified-not-installed'
except BaseException as e:r['status']='failed';r['error']=str(e);raise
finally:(w/'build-003.json').write_text(json.dumps(r,indent=2)+'\n')
