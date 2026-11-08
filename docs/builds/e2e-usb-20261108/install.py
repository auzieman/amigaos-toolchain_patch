"""Host-only file update of the identified, already read-only-mounted lab USB."""
from pathlib import Path,PurePosixPath
import hashlib,json,os,shutil,struct,subprocess,sys,tarfile,zlib
resume = sys.argv[1:] == ["--resume"]
assert not sys.argv[1:] or resume
PROJECT=Path('/home/auzieman/Projects/tabor-spe-toolchain')
work=PROJECT/'work/e2e-usb-20261108';docs=PROJECT/'docs/builds/e2e-usb-20261108'
boot=Path('/mnt/tabor-e2e-boot');root=Path('/mnt/tabor-e2e-root')
receipt=json.loads((docs/'receipt.json').read_text());release=receipt['kernel_release']
backup=work/'usb-backup';stage=work/'unpacked'
r={'status':'started','kernel_release':release,'partition_table_changed':False,'root_userspace_replaced':False,'backup':str(backup),'boot_defaults_in_firmware_changed':False,'verified_files':{}}
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def identity():
 props=dict(x.split('=',1) for x in subprocess.check_output(['udevadm','info','--query=property','--name=/dev/sdb'],text=True).splitlines() if '=' in x)
 assert props.get('ID_BUS')=='usb' and props.get('ID_SERIAL_SHORT')=='03001919041721081205'
 assert subprocess.check_output(['lsblk','-n','-o','PARTUUID','/dev/sdb2'],text=True).strip()=='a1221105-02'
 # Reject mount substitution; never write a path that is not the intended partition.
 for target,dev in [(boot,'/dev/sdb1'),(root,'/dev/sdb2')]:
  assert subprocess.check_output(['findmnt','-n','-o','SOURCE','--target',str(target)],text=True).strip()==dev
 return props['ID_SERIAL_SHORT']
def image_crc(blob):
 magic,hcrc,stamp,size,load,entry,dcrc=struct.unpack_from('>7I',blob);h=bytearray(blob[:64]);h[4:8]=b'\0'*4
 assert magic==0x27051956 and len(blob)==size+64 and zlib.crc32(h)==hcrc and zlib.crc32(blob[64:])==dcrc

def atomic_copy(src,dst):
 for parent in dst.parents:
  if parent==root or parent==boot:break
  assert not parent.is_symlink(),str(parent)
 dst.parent.mkdir(parents=True,exist_ok=True)
 temp=dst.with_name(dst.name+'.e2e-next');assert not temp.exists()
 shutil.copy2(src,temp)
 with temp.open('rb') as f:os.fsync(f.fileno())
 assert sha(src)==sha(temp);os.replace(temp,dst);assert sha(src)==sha(dst)
 r['verified_files'][str(dst)]=sha(dst)

assert os.geteuid()==0
try:
 r['serial']=identity()
 assert receipt['status']=='complete-kernel-modules-firmware-bundle-not-installed'
 assert sha(work/'update.tar')==receipt['tar_sha256']
 if resume:
  previous=json.loads((docs/'usb-install.json').read_text())
  assert previous['status']=='started' and previous['kernel_release']==release
  for name,digest in previous['verified_files'].items():
   p=Path(name);assert p.is_relative_to(boot) or p.is_relative_to(root)
   assert sha(p)==digest,name
  r['resumed_after_pre_activation_pause']=True
 else:
  assert not backup.exists() and not stage.exists() and not (root/'lib/modules'/release).exists()
  assert not (boot/'boot/e2e').exists()
 expected={'boot.scr':'e5905665216e170cb4c6af4954f8ebee35810dc3427606bac9d485703f6d184d','boot/uImage-modular':'6c289f999b9cc707d519489d417d00d68a3e722c81c0abad1a05685271ac12c9','boot/tabor.dtb':'e97a43fcbfee804d7fece5c9010f188c73c5bdaa63d3213f17deda77cd16726d','boot/uRamdisk-fw':'239e7aa7140b5e5474259fd2e12c7396243067acc5385a43cd37e0d219236745'}
 for n,h in expected.items():assert sha(boot/n)==h,n
 init_before=sha(root/'init')
 backup.mkdir(exist_ok=resume);stage.mkdir(exist_ok=resume)
 for n in ['boot.scr','boot.cmd','boot/uImage-modular','boot/tabor.dtb','boot/uRamdisk-fw']:
  p=backup/'fat'/n;p.parent.mkdir(parents=True,exist_ok=True)
  if resume:assert sha(p)==sha(boot/n)
  else:shutil.copy2(boot/n,p)
  assert sha(p)==sha(boot/n)
 with tarfile.open(work/'update.tar') as t:
  for m in t.getmembers():
   p=PurePosixPath(m.name)
   assert not p.is_absolute() and '..' not in p.parts and (m.isfile() or m.isdir()),m.name
  t.extractall(stage,filter='data')
 for n,h in receipt['bundle_files_sha256'].items():assert sha(stage/n)==h,n
 blob=(work/'boot.scr').read_bytes();image_crc(blob);assert blob[72:]==(docs/'boot.cmd').read_bytes()
 image_crc((stage/'fat/boot/e2e/uImage').read_bytes())
 r['initial_boot_sha256']=expected
 # All preconditions and backups completed before either filesystem becomes writable.
 identity()
 subprocess.run(['mount','-o','remount,rw',str(root)],check=True)
 subprocess.run(['mount','-o','remount,rw',str(boot)],check=True)
 for n,h in receipt['bundle_files_sha256'].items():
  rel=PurePosixPath(n);assert rel.parts[0] in ['root','fat']
  dest=(root if rel.parts[0]=='root' else boot).joinpath(*rel.parts[1:]);src=stage/n
  if dest.exists():
   assert dest.is_file()
   if dest.is_symlink():
    assert dest.resolve().is_relative_to(root.resolve()),str(dest)
    assert sha(dest)==h,'firmware alias contents differ: '+str(dest)
    continue
   if sha(dest)==h:continue
   old=backup/rel;old.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,old)
  atomic_copy(src,dest)
 # Keep an exact selectable copy of the old script; it references retained old payloads.
 atomic_copy(backup/'fat/boot.scr',boot/'boot-before-e2e.scr')
 atomic_copy(backup/'fat/boot.cmd',boot/'boot-before-e2e.cmd')
 atomic_copy(work/'boot.scr',boot/'boot-e2e.scr')
 atomic_copy(docs/'boot.cmd',boot/'boot-e2e.cmd')
 # Record selected artifact identities in the existing rescue root, no service/account changes.
 marker=root/'etc/tabor/e2e-boot.json';marker.parent.mkdir(parents=True,exist_ok=True)
 marker.write_text(json.dumps({'kernel_release':release,'module_sha256':receipt['module_verification']['module_sha256'],'tar_sha256':receipt['tar_sha256'],'mode':'kernel-modules-firmware coherent physical test; existing rescue userspace'},indent=2)+'\n')
 os.chmod(marker,0o644)
 os.sync()
 # Switch the ordinary saved /boot.scr selection only after every payload is verified.
 atomic_copy(docs/'boot.cmd',boot/'boot.cmd')
 atomic_copy(work/'boot.scr',boot/'boot.scr')
 os.sync()
 assert sha(root/'init')==init_before
 assert sha(boot/'boot/uImage-modular')==expected['boot/uImage-modular']
 assert sha(boot/'boot/tabor.dtb')==expected['boot/tabor.dtb']
 assert sha(boot/'boot/uRamdisk-fw')==expected['boot/uRamdisk-fw']
 for n,h in receipt['bundle_files_sha256'].items():
  part=PurePosixPath(n);target=(root if part.parts[0]=='root' else boot).joinpath(*part.parts[1:]);assert sha(target)==h,n
 r.update(status='matched-boot-set-installed-readback-verified',init_sha256=init_before,selected_boot_scr_sha256=sha(boot/'boot.scr'),rollback_boot_scr_sha256=sha(boot/'boot-before-e2e.scr'))
finally:
 os.sync()
 for target in [boot,root]:
  subprocess.run(['mount','-o','remount,ro',str(target)],check=False)
 (docs/'usb-install.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:v for k,v in r.items() if k!='verified_files'},indent=2))
