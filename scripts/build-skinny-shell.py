#!/usr/bin/env python3
"""Build a static, source-pinned BusyBox shell and deterministic initramfs."""
import argparse,hashlib,json,os,stat,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for name in ['project','cache','work','tools','sysroot']:p.add_argument('--'+name,type=Path,required=True)
p.add_argument('--image-id',required=True);a=p.parse_args()
profile=json.loads((a.project/'profiles/toolchain-bootstrap.json').read_text());spec=profile['busybox'];archive=a.cache/spec['filename']
if hashlib.sha256(archive.read_bytes()).hexdigest()!=spec['sha256']:p.error('BusyBox archive mismatch')
if not (a.sysroot/'usr/lib/libc.a').is_file() and not (a.sysroot/'lib/libc.a').is_file():p.error('experimental static glibc not installed')
a.work.mkdir(exist_ok=False);receipt={'status':'started','image_id':a.image_id,'source_sha256':spec['sha256'],'commands':[],'boot_tested':False}
with (a.work/'build.log').open('w') as log:
 def run(cmd,cwd=None):receipt['commands'].append(cmd);subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
 try:
  run(['tar','-xjf',str(archive),'-C',str(a.work)])
  source=a.work/('busybox-'+spec['version']);output=a.work/'obj';output.mkdir()
  cross=str(a.tools/'bin/powerpc-linux-gnuspe-')
  flags='--sysroot='+str(a.sysroot)+' -mcpu=8548 -mabi=spe -mspe -mfloat-gprs=double'
  make=['make','-C',str(source),'O='+str(output),'CROSS_COMPILE='+cross,'EXTRA_CFLAGS='+flags,'EXTRA_LDFLAGS=--sysroot='+str(a.sysroot)]
  run(make+['KCONFIG_ALLCONFIG='+str(a.project/'profiles/images/busybox-shell.config'),'allnoconfig'])
  config=(output/'.config').read_text()
  for required in ['CONFIG_STATIC=y','CONFIG_ASH=y','CONFIG_SH_IS_ASH=y','CONFIG_MOUNT=y']:
   if required not in config:raise RuntimeError('Missing shell configuration: '+required)
  run(make+['-j2'])
  binary=output/'busybox'
  headers=subprocess.check_output(['powerpc-linux-gnu-readelf','-l',str(binary)],text=True)
  if 'INTERP' in headers:raise RuntimeError('Shell must be statically linked')
  runtime=a.work/'busybox';run(['powerpc-linux-gnu-strip','-o',str(runtime),str(binary)])
  init=b'''#!/bin/sh
/bin/busybox mount -t proc proc /proc
/bin/busybox mount -t sysfs sysfs /sys
/bin/busybox mount -t devtmpfs devtmpfs /dev
printf '\\nA1222 experimental SPE bootstrap shell\\n'
printf 'SHELL_READY\\n'
exec /bin/sh -i
'''
  with (a.work/'shell.cpio').open('wb') as out:
   def entry(name,mode,data=b'',major=0,minor=0):
    name=name.encode()+b'\0';fields=[0,mode,0,0,1,0,len(data),0,0,major,minor,len(name),0]
    header=b'070701'+''.join(f'{v:08x}' for v in fields).encode();out.write(header+name+b'\0'*(-(len(header)+len(name))%4));out.write(data+b'\0'*(-len(data)%4))
   for directory in ['bin','dev','proc','sys','tmp','root','etc']:entry(directory,stat.S_IFDIR|0o755)
   entry('dev/console',stat.S_IFCHR|0o600,major=5,minor=1)
   entry('bin/busybox',stat.S_IFREG|0o755,runtime.read_bytes())
   for name in ['sh','ash','cat','echo','printf','ls','pwd','mkdir','mount','umount','uname','head','sleep','true','false','test']:entry('bin/'+name,stat.S_IFLNK|0o777,b'busybox')
   entry('init',stat.S_IFREG|0o755,init);entry('TRAILER!!!',0)
  receipt['config_sha256']=hashlib.sha256((output/'.config').read_bytes()).hexdigest()
  receipt['busybox_sha256']=hashlib.sha256(runtime.read_bytes()).hexdigest();receipt['busybox_bytes']=runtime.stat().st_size
  receipt['initramfs_sha256']=hashlib.sha256((a.work/'shell.cpio').read_bytes()).hexdigest();receipt['initramfs_bytes']=(a.work/'shell.cpio').stat().st_size
  receipt['status']='static-shell-initramfs-built'
 except Exception as exc:receipt['status']='failed';receipt['error']=str(exc);raise
 finally:(a.work/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'])
