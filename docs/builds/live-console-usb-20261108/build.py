"""R730 root-only, file-backed console live image; never writes a physical disk."""
from pathlib import Path
import hashlib,json,os,shutil,struct,subprocess,zlib
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
b=Path('/srv/data1/tabor-build/linux-live-001');w=b/'work/live-console-usb-20261108-001';w.mkdir(exist_ok=False)
inputs=Path('/home/owner/live-console-usb-20261108')
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
r={'status':'building','physical_usb_written':False,'hardware_booted':False,'desktop_included':False,'gcc14_userspace_claimed':False,'default_release':'6.12.113-tabor-e2e-008','rollback_release':'6.12.113-tabor-e2e-007','root_partuuid':'a1221108-02'}
log=(w/'build.log').open('w')
def run(c): subprocess.run(list(map(str,c)),check=True,stdout=log,stderr=subprocess.STDOUT)
def crc(p):
 d=p.read_bytes();h=bytearray(d[:64]);magic,hcrc,_,size,_,_,dcrc=struct.unpack_from('>7I',h);h[4:8]=bytes(4)
 assert magic==0x27051956 and len(d)==size+64 and zlib.crc32(h)==hcrc and zlib.crc32(d[64:])==dcrc
try:
 root=w/'root';run(['cp','-a','--reflink=auto',b/'work/layered-rescue-20261105-001/root',root])
 run(['python3',inputs/'configure-rescue-admin.py','--root',root,'--receipt',w/'admin-config.json'])
 fatdir=w/'fat';(fatdir/'boot').mkdir(parents=True)
 for number in ['007','008']:
  parent=b/('work/e2e-usb-20261108-'+number);d=json.loads((parent/'receipt.json').read_text());assert d['status']=='complete-kernel-modules-firmware-bundle-not-installed'
  for rel,h in d['bundle_files_sha256'].items(): assert sha(parent/'bundle'/rel)==h,rel
  run(['cp','-a',str(parent/'bundle/root')+'/.',root])
  shutil.copytree(parent/'bundle/fat/boot/e2e',fatdir/('boot/e2e-'+number))
  r['candidate_'+number]={'receipt_sha256':sha(parent/'receipt.json'),'module_sha256':d['module_verification']['module_sha256']}
 fw=Path('/home/owner/early-polaris-firmware-20261105-001/uRamdisk-fw');assert sha(fw)=='239e7aa7140b5e5474259fd2e12c7396243067acc5385a43cd37e0d219236745'
 shutil.copy2(fw,fatdir/'boot/uRamdisk-fw');crc(fatdir/'boot/uRamdisk-fw')
 bb=b/'work/tabor-modular-stage-20261105-001/busybox-modules';assert sha(bb)=='4de0ebee34a1798b66c5dd8533cb278c3ab73331237d7622414780b2455286ea'
 (root/'sbin').mkdir(exist_ok=True);shutil.copy2(bb,root/'sbin/busybox-modules')
 for name in ['modprobe','lsmod','insmod','sha256sum']:
  p=root/'sbin'/name
  if not p.exists() and not p.is_symlink():p.symlink_to('busybox-modules')
 bash=b/'work/debian-bash-510/bash-static_5.2.37-2_powerpcspe.deb';assert sha(bash)=='7512c35f55b1bf6012b902b25ad5fa86a201e9099fb3dd0a64096aff5a020c1c'
 run(['dpkg-deb','-x',bash,w/'bash-extracted']);binary=w/'bash-extracted/bin/bash-static'
 if not binary.exists():binary=w/'bash-extracted/usr/bin/bash-static'
 assert sha(binary)=='79c588b7e21b8dfb1f6e68443fb9c84db09681c94c6698e8960f2db155d5b736';shutil.copy2(binary,root/'bin/bash')
 for source,name,h in [(Path('/home/owner/fb-fractal-20261108/fb-fractal'),'fb-fractal','16dd8c21f9b0e1e3c120934ea0c1ff0178a5f0dd2fe09335a8a2280c73abd97f'),(Path('/home/owner/fb-cube-20261108/fb-cube'),'fb-cube','66fd49b68f28710759364d84320bcac46621a5527727ebc2c82955c95b8a9c92')]:
  assert sha(source)==h;shutil.copy2(source,root/'bin'/name);(root/'bin'/name).chmod(0o755)
 data=root/'usr/share/tabor';data.mkdir(parents=True,exist_ok=True)
 counts=Path('/home/owner/fb-fractal-20261108/counts.bin');assert sha(counts)=='927af0852454fd8c2324a27158d36f31af1e0386019a653070d625921de56d50';shutil.copy2(counts,data/'fractal-counts.bin')
 # Keep bootstrap PID1/shell untouched; put SSH runtime logs in tmpfs.
 p=root/'etc/start-ssh';s=p.read_text();s=s.replace('umask 077','umask 077\ngrep -q " /run tmpfs " /proc/mounts || mount -t tmpfs -o size=32m tmpfs /run');s=s.replace('-E /tmp/sshd.log','-E /run/sshd.log');p.write_text(s);p.chmod(0o755)
 for key in (root/'etc/ssh').glob('ssh_host_*'):key.unlink()
 run(['ssh-keygen','-q','-t','ed25519','-N','','-f',root/'etc/ssh/ssh_host_ed25519_key'])
 r['ssh_host_public_key']=(root/'etc/ssh/ssh_host_ed25519_key.pub').read_text().strip()
 for name,body in [('fractal-screen','exec /bin/fb-fractal --draw /usr/share/tabor/fractal-counts.bin /run/fractal-console.backup'),('cube-screen','exec /bin/fb-cube --animate /run/cube-console-$$.backup')]:
  p=root/'bin'/name;p.write_text('#!/bin/sh\n'+body+'\n');p.chmod(0o755)
 for number,name in [('008','boot'),('007','boot-007-rollback')]:
  cmd=f'''# A1222 console live test; GPU load remains manual, no firmware saveenv.
echo Booting Tabor console candidate {number}
if usb reset; then
 if fatload usb 0:1 0x04000000 /boot/e2e-{number}/uImage; then
  if iminfo 0x04000000; then
   if fatload usb 0:1 0x08000000 /boot/e2e-{number}/tabor.dtb; then
    setenv bootargs root=PARTUUID=a1221108-02 rootfstype=ext4 rootwait rw init=/init mem=3500M console=ttyS0,115200 console=tty0 loglevel=8 ignore_loglevel panic=-1
    if fatload usb 0:1 0x0a000000 /boot/uRamdisk-fw; then
     if iminfo 0x0a000000; then
      bootm 0x04000000 0x0a000000 0x08000000
     fi
    fi
   fi
  fi
 fi
fi
echo Boot returned; saved firmware settings unchanged.
'''
  p=fatdir/(name+'.cmd');p.write_text(cmd)
  run(['mkimage','-A','ppc','-O','linux','-T','script','-C','none','-n','Tabor console '+number,'-d',p,fatdir/(name+'.scr')]);crc(fatdir/(name+'.scr'))
  for file in (fatdir/('boot/e2e-'+number)).iterdir():
   if file.name=='uImage':crc(file)
 readme='Tabor A1222 console live image: candidate008, rollback007. Not a complete Debian desktop or accelerated GL acceptance.\nBoot: usb reset; fatload usb 0:1 0x09000000 /boot.scr; source 0x09000000\nRollback: fatload usb 0:1 0x09000000 /boot-007-rollback.scr; source 0x09000000\nSSH key-only tabor/root, wired DHCP. GPU is initially unloaded; use protected off-board first-bind test before framebuffer demos.\nConsole commands after healthy GPU init: bash, fractal-screen, cube-screen.\nFractal restore: /bin/fb-fractal --restore /run/fractal-console.backup\nRetained known-working boot limits include mem=3500M. No firmware changes or internal-disk installation.\n'
 (fatdir/'BOOT-README.txt').write_text(readme);(data/'LIVE-README.txt').write_text(readme)
 fat=w/'boot.fat';ext=w/'root.ext4'
 with fat.open('wb') as f:f.truncate(256*1024**2)
 run(['mkfs.fat','-F','32','-n','TABOR_BOOT',fat]);run(['mcopy','-s','-i',fat,str(fatdir/'boot'),'::/'])
 for p in fatdir.iterdir():
  if p.is_file():run(['mcopy','-i',fat,p,'::/'+p.name])
 for p in fatdir.rglob('*'):
  if p.is_file():assert subprocess.check_output(['mtype','-i',str(fat),'::/'+str(p.relative_to(fatdir))])==p.read_bytes()
 with ext.open('wb') as f:f.truncate(4*1024**3)
 run(['mkfs.ext4','-F','-L','TABOR_CONSOLE','-U','a1221108-0000-4000-8000-000000000002','-d',root,ext]);run(['e2fsck','-f','-n',ext]);run(['fsck.fat','-n',fat])
 image=w/'tabor-console-008.img';first=2048;second=first+fat.stat().st_size//512;total=second+ext.stat().st_size//512
 mbr=bytearray(512);struct.pack_into('<I',mbr,440,0xa1221108)
 for i,active,kind,start,size in [(0,128,12,first,second-first),(1,0,131,second,total-second)]:struct.pack_into('<B3sB3sII',mbr,446+i*16,active,b'\xfe\xff\xff',kind,b'\xfe\xff\xff',start,size)
 mbr[510:512]=b'\x55\xaa'
 with image.open('wb') as dst:
  dst.truncate(total*512);dst.write(mbr)
  for start,p in [(first,fat),(second,ext)]:
   dst.seek(start*512)
   with p.open('rb') as src:
    while chunk:=src.read(4*1024**2):
     if any(chunk):dst.write(chunk)
     else:dst.seek(len(chunk),1)
 r.update(status='console-image-built-not-booted',image=str(image),image_bytes=image.stat().st_size,image_sha256=sha(image),boot_files_sha256={str(p.relative_to(fatdir)):sha(p) for p in fatdir.rglob('*') if p.is_file()},root_init_sha256=sha(root/'init'),recipe_sha256=sha(Path(__file__)))
except BaseException as e:r.update(status='failed',error=str(e));raise
finally:(w/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');log.close()
print(json.dumps({k:r[k] for k in ['status','image','image_bytes','image_sha256']}))
