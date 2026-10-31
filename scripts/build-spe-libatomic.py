#!/usr/bin/env python3
import argparse,hashlib,json,os,subprocess
from pathlib import Path
p=argparse.ArgumentParser()
for n in ['project','cache','tools','sysroot','work']:p.add_argument('--'+n,type=Path,required=True)
a=p.parse_args();a.work.mkdir(parents=True,exist_ok=False);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=json.loads((a.project/'profiles/toolchain-bootstrap.json').read_text())['gcc'];archive=a.cache/spec['filename'];assert hashlib.sha512(archive.read_bytes()).hexdigest()==spec['sha512']
stage=a.work/'stage';cc=a.tools/'bin/powerpc-linux-gnuspe-gcc';flags=['--sysroot='+str(a.sysroot),'-mcpu=8548','-mabi=spe','-mspe','-mfloat-gprs=double','-mlong-double-128','-O2','-fPIC']
env=os.environ.copy();env.update(PATH=str(a.tools/'bin')+':'+env['PATH'],CC=str(cc),CFLAGS=' '.join(flags),AR=str(a.tools/'bin/powerpc-linux-gnuspe-ar'),RANLIB=str(a.tools/'bin/powerpc-linux-gnuspe-ranlib'))
r={'status':'running','source_sha256':sha(archive),'flags':flags,'commands':[]}
try:
 with (a.work/'build.log').open('w') as log:
  def run(cmd,cwd):r['commands'].append(list(map(str,cmd)));subprocess.run(list(map(str,cmd)),cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
  run(['tar','-xf',archive,'-C',a.work],a.work);src=a.work/('gcc-'+spec['version']);obj=a.work/'obj';obj.mkdir()
  run([src/'libatomic/configure','--host=powerpc-linux-gnuspe','--target=powerpc-linux-gnuspe','--build=x86_64-linux-gnu','--prefix=/usr','--libdir=/usr/lib','--enable-shared','--disable-multilib'],obj)
  run(['make','-j4'],obj);run(['make','DESTDIR='+str(stage),'install'],obj)
  run([cc,*flags,a.project/'bench/atomic64-check.c','-L'+str(stage/'usr/lib'),'-latomic','-pthread','-o',a.work/'atomic64-check'],a.work)
  lib=stage/'usr/lib/libatomic.so.1.2.0';assert lib.is_file();data=lib.read_bytes();assert data[:6]==b'\x7fELF\x01\x02';r.update(status='built-not-executed',lib_sha256=sha(lib),probe_sha256=sha(a.work/'atomic64-check'))
except Exception as e:r.update(status='failed',error=str(e));raise
finally:(a.work/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
print(r['status'])
