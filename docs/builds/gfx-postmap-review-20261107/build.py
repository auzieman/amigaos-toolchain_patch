import json,hashlib,subprocess,shutil
from pathlib import Path
b=Path('/base');w=Path('/candidate');inp=Path('/inputs');ref=b/'work/gfx-map-stage-20261107-001';project=b/'gfx-map-stage-20261107-001-project'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r={'status':'started','hardware_tested':False,'kernel':'6.12.113-tabor-modular','new_patches':{},'commands':[]}
log=(w/'build.log').open('w')
def run(cmd,cwd=None):
 r['commands'].append(cmd);log.write(repr(cmd)+'\n');log.flush();subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
try:
 lock=json.loads((inp/'source-lock.json').read_text())['components']['linux']
 for f in lock['files']:assert sha(b/'tabor-source-cache'/f['filename'])==f['sha256']
 parent=json.loads((ref/'receipt.json').read_text())
 for name,digest in parent['patches'].items():assert sha(project/'patches/linux'/name)==digest
 run(['dpkg-source','--no-check','-x',str(b/'tabor-source-cache'/lock['dsc']),str(w/'source')])
 for name in parent['patches']:
  p=project/'patches/linux'/name;run(['git','apply','--check',str(p)],w/'source');run(['git','apply',str(p)],w/'source')
 review=json.loads((inp/'receipt.json').read_text())
 for name,digest in review['source_inputs'].items():assert sha(w/'source'/name)==digest,name
 for name,digest in review['patches'].items():
  p=inp/name;assert sha(p)==digest;run(['git','apply','--check',str(p)],w/'source');run(['git','apply',str(p)],w/'source');r['new_patches'][name]=digest
 (w/'output').mkdir();shutil.copyfile(ref/'output/.config',w/'output/.config')
 mk=['make','-C',str(w/'source'),'O='+str(w/'output'),'ARCH=powerpc','CROSS_COMPILE=powerpc-linux-gnu-']
 run(mk+['olddefconfig']);assert sha(w/'output/.config')==parent['config_sha256']
 run(mk+['-j4','modules_prepare'])
 # Export ABI data from the exact unchanged accepted kernel build. No exports or config change here.
 shutil.copyfile(ref/'output/Module.symvers',w/'output/Module.symvers')
 r['kernel_symvers_sha256']=sha(ref/'output/Module.symvers')
 run(mk+['-j4','M=drivers/gpu/drm/amd/amdgpu','modules'])
 module=w/'output/drivers/gpu/drm/amd/amdgpu/amdgpu.ko';r['module_sha256']=sha(module)
 run(['powerpc-linux-gnu-readelf','-h',str(module)]);run(['powerpc-linux-gnu-readelf','-p','.modinfo',str(module)])
 r['status']='compiled-not-installed'
except Exception as e:r['status']='failed';r['error']=str(e);raise
finally:(w/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');log.close()
