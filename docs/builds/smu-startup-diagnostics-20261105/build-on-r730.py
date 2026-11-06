import subprocess,pathlib,shutil,json,hashlib
b=pathlib.Path('/base');p=b/'smu-diagnostics-project-20261105-003';w=b/'work/tabor-smu-diagnostics-20261105-003';reference=b/'work/tabor-modular-20261105-003/output'
image='sha256:2781e11839beffa351f8c411d71b7e2bd1ae0336d24c60b407778c3350dd9da0'
shutil.copytree(b/'modular-project-20261105-001',p,symlinks=True)
shutil.copy2('/diagnostic.patch',p/'patches/linux/0003-smu-diagnostics-experiment.patch')
with (p/'patches/linux/series').open('a') as f:f.write('0003-smu-diagnostics-experiment.patch\n')
subprocess.run(['python3',str(p/'scripts/debian-iterate.py'),'--project',str(p),'--cache',str(b/'tabor-source-cache'),'--work',str(w),'--component','linux','--mode','configure','--kernel-profile','tabor-modular','--kernel-config',str(reference/'.config'),'--jobs','4','--image-id',image],check=True)
# Copy accepted build outputs to a disposable candidate; never mutate reference.
shutil.copytree(reference,w/'output',symlinks=True,dirs_exist_ok=True,ignore=lambda directory,names: {"source"} if pathlib.Path(directory)==reference else set())
make=['make','-C',str(w/'source'),'O='+str(w/'output'),'ARCH=powerpc','CROSS_COMPILE=powerpc-linux-gnu-','-j4','drivers/gpu/drm/amd/amdgpu/amdgpu.ko']
r={'status':'started','reference':'tabor-modular-20261105-003','target':'amdgpu.ko','image_id':image,'command':make,'hardware_tested':False}
try:
 with (w/'module-build.log').open('w') as log:subprocess.run(make,stdout=log,stderr=subprocess.STDOUT,check=True)
 f=w/'output/drivers/gpu/drm/amd/amdgpu/amdgpu.ko';r.update(status='module-compiled',sha256=hashlib.sha256(f.read_bytes()).hexdigest())
 assert (w/'output/.config').read_bytes()==(reference/'.config').read_bytes()
 assert (w/'output/Module.symvers').read_bytes()==(reference/'Module.symvers').read_bytes()
 r['reference_config_and_symbols_match']=True
finally:(w/'module-receipt.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
