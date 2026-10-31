#!/usr/bin/env python3
"""Build a static, source-pinned BusyBox shell and deterministic initramfs."""
import argparse,hashlib,json,os,re,stat,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for name in ['project','cache','work','tools','sysroot']:p.add_argument('--'+name,type=Path,required=True)
p.add_argument('--image-id',required=True)
p.add_argument('--variant',choices=['shell','rescue'],default='shell');a=p.parse_args()
profile=json.loads((a.project/'profiles/toolchain-bootstrap.json').read_text());spec=profile['busybox'];archive=a.cache/spec['filename']
if hashlib.sha256(archive.read_bytes()).hexdigest()!=spec['sha256']:p.error('BusyBox archive mismatch')
if not (a.sysroot/'usr/lib/libc.a').is_file() and not (a.sysroot/'lib/libc.a').is_file():p.error('experimental static glibc not installed')
a.work.mkdir(exist_ok=False);receipt={'status':'started','variant':a.variant,'image_id':a.image_id,'source_sha256':spec['sha256'],'commands':[],'boot_tested':False}
with (a.work/'build.log').open('w') as log:
 def run(cmd,cwd=None,input=None):receipt['commands'].append(cmd);subprocess.run(cmd,cwd=cwd,input=input,stdout=log,stderr=subprocess.STDOUT,check=True)
 try:
  run(['tar','-xjf',str(archive),'-C',str(a.work)])
  source=a.work/('busybox-'+spec['version']);output=a.work/'obj';output.mkdir()
  cross=str(a.tools/'bin/powerpc-linux-gnuspe-')
  policy=json.loads((a.project/'profiles/images/a1222-minimal.json').read_text())['build_policy']
  flags='--sysroot='+str(a.sysroot)+' -isystem '+str(a.sysroot/'usr/include')+' -B'+str(a.sysroot/'usr/lib')+'/ '+' '.join(policy['target_runtime_cflags'])
  receipt['target_runtime_cflags']=policy['target_runtime_cflags']
  make=['make','-C',str(source),'O='+str(output),'CROSS_COMPILE='+cross,'CONFIG_EXTRA_CFLAGS='+flags,'CONFIG_EXTRA_LDFLAGS=--sysroot='+str(a.sysroot)]
  run(make+['allnoconfig'])
  # BusyBox set_no overrides seeded booleans; apply the seed after allnoconfig.
  seed=a.project/'profiles/images'/('busybox-rescue.config' if a.variant=='rescue' else 'busybox-shell.config')
  entries={line.split('=',1)[0]:line for line in seed.read_text().splitlines() if line.startswith('CONFIG_')}
  config_path=output/'.config';lines=config_path.read_text().splitlines();merged=[]
  for line in lines:
   match=re.match(r'(CONFIG_[A-Z0-9_]+)=|# (CONFIG_[A-Z0-9_]+) is not set',line)
   key=(match.group(1) or match.group(2)) if match else None
   merged.append(entries.pop(key,line))
  merged.extend(entries.values());config_path.write_text('\n'.join(merged)+'\n')
  # Newly enabled applets introduce numeric/string settings. Accept defaults
  # noninteractively after applying our explicit seed; never leave a lab job
  # waiting for an interactive Kconfig prompt.
  run(make+['oldconfig'],input=b'\n'*65536)
  receipt['config_seed_sha256']=hashlib.sha256(seed.read_bytes()).hexdigest()
  config=(output/'.config').read_text()
  for required in ['CONFIG_STATIC=y','CONFIG_ASH=y','CONFIG_SH_IS_ASH=y','CONFIG_MOUNT=y']:
   if required not in config:raise RuntimeError('Missing shell configuration: '+required)
  if a.variant=='rescue':
   for key in ['CONFIG_UDHCPC','CONFIG_IP','CONFIG_PS','CONFIG_DMESG','CONFIG_VI']:
    if key+'=y' not in config:raise RuntimeError('Missing rescue applet: '+key)
  run(make+['-j2'])
  binary=output/'busybox'
  headers=subprocess.check_output(['powerpc-linux-gnu-readelf','-l',str(binary)],text=True)
  if 'INTERP' in headers:raise RuntimeError('Shell must be statically linked')
  runtime=a.work/'busybox';run(['powerpc-linux-gnu-strip','-o',str(runtime),str(binary)])
  init_source=a.project/'boot/init-shell.c';init_binary=a.work/'init'
  run([cross+'gcc']+flags.split()+['-Os','-static','-s',str(init_source),'-o',str(init_binary)])
  init_headers=subprocess.check_output(['powerpc-linux-gnu-readelf','-l',str(init_binary)],text=True)
  if 'INTERP' in init_headers:raise RuntimeError('Init must be statically linked')
  init=init_binary.read_bytes()
  receipt['init_source_sha256']=hashlib.sha256(init_source.read_bytes()).hexdigest()
  receipt['init_sha256']=hashlib.sha256(init).hexdigest()
  with (a.work/'shell.cpio').open('wb') as out:
   def entry(name,mode,data=b'',major=0,minor=0):
    name=name.encode()+b'\0';fields=[0,mode,0,0,1,0,len(data),0,0,major,minor,len(name),0]
    header=b'070701'+''.join(f'{v:08x}' for v in fields).encode();out.write(header+name+b'\0'*(-(len(header)+len(name))%4));out.write(data+b'\0'*(-len(data)%4))
   for directory in ['bin','sbin','dev','proc','sys','tmp','root','etc']:entry(directory,stat.S_IFDIR|(0o1777 if directory=='tmp' else 0o755))
   entry('dev/console',stat.S_IFCHR|0o600,major=5,minor=1)
   entry('bin/busybox',stat.S_IFREG|0o755,runtime.read_bytes())
   applets=['sh','ash','cat','echo','printf','ls','pwd','mkdir','mount','umount','uname','head','sleep','true','false','test']
   if a.variant=='rescue':
    applets+=['cp','mv','rm','ln','chmod','chown','dmesg','ps','top','free','df','du','date','sync','reboot','poweroff','ip','ifconfig','route','ping','udhcpc','lsusb','lspci','vi','less','find','grep','sed','tar','gzip','gunzip','wc','cut','sort','stty','clear']
   for name in applets:entry('bin/'+name,stat.S_IFLNK|0o777,b'busybox')
   receipt['applets']=applets
   if a.variant=='rescue':
    script=a.project/'boot/udhcpc.script'
    receipt['dhcp_script_sha256']=hashlib.sha256(script.read_bytes()).hexdigest()
    entry('etc/udhcpc.script',stat.S_IFREG|0o755,script.read_bytes())
   entry('init',stat.S_IFREG|0o755,init);entry('TRAILER!!!',0)
  receipt['config_sha256']=hashlib.sha256((output/'.config').read_bytes()).hexdigest()
  receipt['busybox_sha256']=hashlib.sha256(runtime.read_bytes()).hexdigest();receipt['busybox_bytes']=runtime.stat().st_size
  receipt['initramfs_sha256']=hashlib.sha256((a.work/'shell.cpio').read_bytes()).hexdigest();receipt['initramfs_bytes']=(a.work/'shell.cpio').stat().st_size
  receipt['status']='static-shell-initramfs-built'
 except Exception as exc:receipt['status']='failed';receipt['error']=str(exc);raise
 finally:(a.work/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'])
