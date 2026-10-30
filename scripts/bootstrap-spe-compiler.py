#!/usr/bin/env python3
"""Build an isolated historical SPE bootstrap compiler from a pinned archive."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--project',type=Path,required=True)
p.add_argument('--cache',type=Path,required=True)
p.add_argument('--work',type=Path,required=True)
p.add_argument('--prefix',type=Path,required=True)
p.add_argument('--image-id',required=True)
a=p.parse_args()
project,cache,work,prefix=[x.resolve() for x in [a.project,a.cache,a.work,a.prefix]]
for x in [project,cache,prefix]:
 if work.is_relative_to(x) or x.is_relative_to(work):p.error('independent work and install/input paths required')
if prefix.exists():p.error('fresh install prefix required')
spec=json.loads((project/'profiles/toolchain-bootstrap.json').read_text())
archive=cache/spec['gcc']['filename']
if hashlib.sha512(archive.read_bytes()).hexdigest()!=spec['gcc']['sha512']:p.error('archive hash mismatch')
if shutil.disk_usage(work.parent).free<3*1024**3:p.error('at least 3 GiB free required')
work.mkdir(exist_ok=False)
receipt={'status':'started','role':spec['role'],'target':spec['target'],'image_id':a.image_id,'source_sha512':spec['gcc']['sha512'],'commands':[],'runtime_built':False}
def interrupted(signum,frame):raise RuntimeError('Interrupted by signal '+str(signum))
signal.signal(signal.SIGTERM,interrupted)
with (work/'build.log').open('w') as log:
 def run(cmd,cwd=None):
  receipt['commands'].append(cmd);log.write('$ '+repr(cmd)+'\n');log.flush()
  env={**os.environ,'CFLAGS':'-O2 -g0','CXXFLAGS':'-O2 -g0','MAKEINFO':'true'}
  proc=subprocess.Popen(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,env=env,start_new_session=True)
  try:
   while True:
    try:code=proc.wait(timeout=5);break
    except subprocess.TimeoutExpired:
     if shutil.disk_usage(work).free<1024**3:raise RuntimeError('Workspace free-space guard below 1 GiB')
  except BaseException:
   os.killpg(proc.pid,signal.SIGTERM)
   try:proc.wait(timeout=10)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
   raise
  if code:raise RuntimeError('Command failed '+str(code)+': '+repr(cmd))
 try:
  run(['tar','-xJf',str(archive),'-C',str(work)])
  source=work/('gcc-'+spec['gcc']['version']);obj=work/'obj';obj.mkdir()
  flags=['--target='+spec['target'],'--prefix='+str(prefix),'--enable-obsolete','--enable-languages=c','--disable-bootstrap','--disable-multilib','--disable-nls','--disable-shared','--disable-threads','--without-headers','--with-newlib','--disable-libsanitizer','--disable-libssp','--disable-libquadmath','--disable-libgomp','--disable-libatomic','--disable-libvtv','--disable-werror','--with-system-zlib','--with-cpu=8548','--with-float=hard','--enable-e500_double','--with-as=/usr/bin/powerpc-linux-gnu-as','--with-ld=/usr/bin/powerpc-linux-gnu-ld']
  run([str(source/'configure')]+flags,obj)
  run(['make','-j2','all-gcc'],obj)
  run(['make','install-gcc'],obj)
  cc=prefix/'bin'/(spec['target']+'-gcc')
  probe=work/'probe.c';probe.write_text('float addf(float a,float b){return a+b;}\ndouble addd(double a,double b){return a+b;}\n')
  run([str(cc),'-O2','-mcpu=8548','-mabi=spe','-mspe','-mfloat-gprs=double','-S',str(probe),'-o',str(work/'probe.s')])
  asm=(work/'probe.s').read_text()
  if 'efsadd' not in asm or 'efdadd' not in asm:raise RuntimeError('Expected SPE instructions absent')
  receipt['compiler_version']=subprocess.check_output([str(cc),'--version'],text=True)
  receipt['target_macros']=subprocess.check_output([str(cc),'-dM','-E','-x','c','-'],input='',text=True)
  receipt['probe_sha256']=hashlib.sha256((work/'probe.s').read_bytes()).hexdigest()
  receipt['status']='compiler-ready-no-libc'
 except Exception as exc:
  receipt['status']='failed';receipt['error']=str(exc);raise
 finally:(work/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'])
