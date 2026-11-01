#!/usr/bin/env python3
"""Build small GL/X11 demos against a completed source-built SPE Mesa stage."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for n in ['project','tools','sysroot','base-stage','fractal-results','work']:p.add_argument('--'+n,type=Path,required=True)
p.add_argument('--firmware-deb',type=Path);p.add_argument('--notice-dir',type=Path,action='append',default=[]);a=p.parse_args();a.work.mkdir(parents=True,exist_ok=False);stage=a.work/'stage';shutil.copytree(a.base_stage,stage,symlinks=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cc=a.tools/'bin/powerpc-linux-gnuspe-gcc';flags=['--sysroot='+str(a.sysroot),'-mcpu=8548','-mabi=spe','-mspe','-mfloat-gprs=double','-mlong-double-128','-O2','-I'+str(stage/'usr/include')]
stdlib=Path(subprocess.check_output([str(cc),'-print-file-name=libstdc++.so'],text=True).strip()).resolve();assert stdlib.is_file()
r={'stdlib_sha256':sha(stdlib),'status':'started','compiler_sha256':sha(cc),'flags':flags,'commands':[],'sources':{},'physical_boot':False,'hardware_GL_validated':False}
try:
 with (a.work/'build.log').open('w') as log:
  for source,libs in [('gl-spe-demo.c',['-lGL','-lX11','-lstdc++','-lm']),('spe-fractal-view.c',['-lX11']),('x11-window-check.c',['-lX11','-lXcomposite']),('spe-smp-check.c',['-pthread']),('a1222-xorg-config.c',[])]:
   src=a.project/'bench'/source;dest=stage/'usr/bin'/source[:-2];cmd=[str(cc),*flags,str(src),'-L'+str(stage/'usr/lib'),'-Wl,-rpath-link,'+str(stage/'usr/lib'),'-L'+str(stdlib.parent),'-Wl,-rpath-link,'+str(stdlib.parent),*libs,'-o',str(dest)];r['commands'].append(cmd);r['sources'][source]=sha(src);subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
  receipt=json.loads((a.fractal_results/'receipt.json').read_text());f=a.fractal_results/'payload/bin/fractal-test'
  assert sha(f)==receipt['fractal_binary_sha256'];shutil.copy2(f,stage/'usr/bin/fractal-test');(stage/'usr/bin/fractal-test').chmod(0o755);r['freestanding_fractal_sha256']=sha(f)
  notices=stage/'usr/share/licenses/tabor-visual-demos';notices.mkdir(parents=True,exist_ok=True)
  shutil.copy2(a.project/'bench/README.md',notices/'fractal-provenance.md')
  for directory in a.notice_dir:
   for notice in directory.glob('*-copyright'):
    shutil.copy2(notice,notices/(directory.name+'-'+notice.name));r.setdefault('notices',{})[str(notice)]=sha(notice)
  for license_name in ['GPL-2','LGPL-2.1']:
   license_file=Path('/usr/share/common-licenses')/license_name
   assert license_file.is_file();shutil.copy2(license_file,notices/license_name)
  if a.firmware_deb:
   policy=json.loads((a.project/'profiles/images/polaris-firmware.json').read_text());assert sha(a.firmware_deb)==policy['sha256'];r['firmware_package']=policy
   extracted=a.work/'firmware-extracted';subprocess.run(['dpkg-deb','-x',a.firmware_deb,extracted],check=True)
   fw=stage/'lib/firmware/amdgpu';fw.mkdir(parents=True,exist_ok=True)
   selected=sorted((extracted/'usr/lib/firmware/amdgpu').glob('polaris1[01]*'));assert selected
   for file in selected:shutil.copy2(file,fw/file.name);r.setdefault('firmware_files',{})[file.name]=sha(file)
   shutil.copy2(extracted/'usr/share/doc/firmware-amd-graphics/copyright',notices/'firmware-amd-graphics-copyright')
  for script,name in [('boot/run-visual-demos.sh','run-visual-demos'),('boot/start-a1222-x.sh','start-a1222-x'),('boot/start-visual-session.sh','start-visual-session')]:
   shutil.copy2(a.project/script,stage/'usr/bin'/name);(stage/'usr/bin'/name).chmod(0o755)
  for name in ['gl-spe-demo','spe-fractal-view','x11-window-check','spe-smp-check','fractal-test','a1222-xorg-config']:
   file=stage/'usr/bin'/name;header=file.read_bytes()[:20];assert header[:6]==b'\x7fELF\x01\x02' and header[18:20]==b'\x00\x14';r.setdefault('binaries',{})[name]=sha(file)
 r['status']='compiled-not-runtime-tested'
except Exception as e:r['status']='failed';r['error']=str(e);raise
finally:(a.work/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
print(r['status'])
