#!/usr/bin/env python3
"""Run a logged libgcc or modern-glibc bootstrap stage inside the lab container."""
import argparse,hashlib,json,os,re,shutil,signal,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--phase',choices=['libgcc','glibc'],required=True)
p.add_argument('--attempt',type=int,default=1)
p.add_argument('--work',type=Path,default=Path('/work'))
p.add_argument('--project',type=Path,default=Path('/project'))
p.add_argument('--tools',type=Path,default=Path('/tools/reference-001'))
p.add_argument('--sysroot',type=Path,default=Path('/sysroot'))
p.add_argument('--glibc-run',default='glibc-002')
p.add_argument('--image-id',required=True)
a=p.parse_args()
if not re.fullmatch(r'glibc-[0-9]{3}',a.glibc_run):p.error('invalid component run')
if not 1<=a.attempt<=99:p.error('invalid stage attempt')
suffix='' if a.attempt==1 else '-'+str(a.attempt).zfill(3)
receipt_path=a.work/(a.phase+'-stage'+suffix+'.json')
if receipt_path.exists():p.error('refuse to reuse stage receipt/output')
cc=a.tools/'bin/powerpc-linux-gnuspe-gcc'
if not cc.is_file():p.error('SPE bootstrap compiler missing')
flags=['-mcpu=8548','-mabi=spe','-mspe','-mfloat-gprs=double']
receipt={'phase':a.phase,'status':'started','image_id':a.image_id,'commands':[],'spe_abi_validated':False,'shell_booted':False}
def interrupted(signum,frame):raise RuntimeError('Interrupted by signal '+str(signum))
signal.signal(signal.SIGTERM,interrupted)
env={**os.environ,'CFLAGS':'-O2 -g0','CXXFLAGS':'-O2 -g0','MAKEINFO':'true','PATH':str(a.tools/'bin')+os.pathsep+os.environ.get('PATH','')}
with (a.work/(a.phase+'-stage'+suffix+'.log')).open('w') as log:
 def run(cmd,cwd=None):
  receipt['commands'].append(cmd);log.write('$ '+repr(cmd)+'\n');log.flush()
  proc=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  try:
   while True:
    try:code=proc.wait(timeout=5);break
    except subprocess.TimeoutExpired:
     if shutil.disk_usage(a.work).free<1024**3:raise RuntimeError('Stopped below 1 GiB workspace free')
  except BaseException:
   os.killpg(proc.pid,signal.SIGTERM)
   try:proc.wait(timeout=10)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
   raise
  if code:raise RuntimeError('Command failed '+str(code)+': '+repr(cmd))
 try:
  receipt['compiler_version']=subprocess.check_output([str(cc),'--version'],text=True)
  if a.phase=='libgcc':
   for name in ['as','ld','ar','ranlib','nm','objcopy','objdump','strip','readelf']:
    alias=a.tools/'bin'/('powerpc-linux-gnuspe-'+name);target=Path('/usr/bin/powerpc-linux-gnu-'+name)
    if alias.exists() or alias.is_symlink():
     if alias.resolve()!=target.resolve():raise RuntimeError('Unexpected binutils alias: '+str(alias))
    else:alias.symlink_to(target)
   run(['make','-C',str(a.work/'gcc-001/obj'),'-j2','all-target-libgcc'])
   run(['make','-C',str(a.work/'gcc-001/obj'),'install-target-libgcc'])
   library=Path(subprocess.check_output([str(cc)]+flags+['-print-libgcc-file-name'],text=True).strip())
   if not library.is_file():raise RuntimeError('libgcc missing')
   receipt['libgcc_sha256']=hashlib.sha256(library.read_bytes()).hexdigest()
   receipt['status']='static-libgcc-ready'
  else:
   component=a.work/a.glibc_run;source=component/'source';output=component/'output'
   prepared=json.loads((component/'receipt.json').read_text())
   if prepared['status']!='prepared':raise RuntimeError('fresh prepared libc required')
   for name,expected in prepared['patches'].items():
    if hashlib.sha256((a.project/'patches/glibc'/name).read_bytes()).hexdigest()!=expected:raise RuntimeError('Patch changed since preparation: '+name)
   if not (a.sysroot/'usr/include/linux/version.h').is_file():raise RuntimeError('Pinned Linux UAPI headers missing')
   output.mkdir(exist_ok=False)
   macros=subprocess.check_output([str(cc)]+flags+['-dM','-E','-x','c','-'],input='',text=True)
   if '#define __SPE__ 1' not in macros or '#define _SOFT_FLOAT' in macros:raise RuntimeError('SPE hard-float compiler required')
   receipt['compiler_macros']=macros
   env.update({'CC':str(cc)+' --sysroot='+str(a.sysroot),'BUILD_CC':'gcc','CXX':'false','CFLAGS':'-O2 -g0 '+' '.join(flags),'AR':'powerpc-linux-gnu-ar','RANLIB':'powerpc-linux-gnu-ranlib','AS':'powerpc-linux-gnu-as','LD':'powerpc-linux-gnu-ld','NM':'powerpc-linux-gnu-nm','OBJCOPY':'powerpc-linux-gnu-objcopy','STRIP':'powerpc-linux-gnu-strip','OBJDUMP':'powerpc-linux-gnu-objdump','READELF':'powerpc-linux-gnu-readelf'})
   run([str(source/'configure'),'--build=x86_64-linux-gnu','--host=powerpc-linux-gnuspe','--prefix=/usr','--with-headers='+str(a.sysroot/'usr/include'),'--disable-nscd','--disable-werror','--enable-kernel=3.2'],output)
   receipt['status']='configured'
   run(['make','-j2'],output)
   receipt['status']='compiled'
   run(['make','install','install_root='+str(a.sysroot)],output)
   receipt['status']='installed-experimental-libc'
 except Exception as exc:
  receipt['status']='failed';receipt['error']=str(exc);raise
 finally:receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'])
