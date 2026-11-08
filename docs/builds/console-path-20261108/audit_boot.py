"""R730 root: read-only SanDisk console/login inspection; no journal replay."""
from pathlib import Path
import subprocess,json,os,hashlib
W=Path('/srv/data1/tabor-build/source-review/console-path-20261108');W.mkdir(exist_ok=True)
d=json.loads(subprocess.check_output(['lsblk','--tree','-J','-o','NAME,PATH,SERIAL,TRAN,PARTUUID,MOUNTPOINTS','/dev/sde'],text=True))['blockdevices'][0]
assert d['serial']=='03001919041721081205'and d['tran']=='usb'
assert d['children'][1]['partuuid']=='a1221105-02'
for c in d['children']:assert not any(c['mountpoints'])
root=Path('/mnt/tabor-console-root');boot=Path('/mnt/tabor-console-boot')
for p in [root,boot]:p.mkdir(exist_ok=True)
subprocess.run(['mount','-o','ro,noload','/dev/sde2',str(root)],check=True)
try:
 subprocess.run(['mount','-o','ro','/dev/sde1',str(boot)],check=True)
 try:
  out={'usb_written':False,'journal_replay':False,'identity':d,'files':{},'symlinks':{}}
  for rel in ['etc/inittab','etc/systemd/system/default.target','etc/systemd/system/getty.target.wants/getty@tty1.service','sbin/init','init','etc/init.d/rcS']:
   p=root/rel
   if p.is_symlink():out['symlinks'][rel]=os.readlink(p);continue
   if not p.is_file():continue
   b=p.read_bytes();out['files'][rel]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'text':b.decode(errors='replace')[:16000] if b[:4]!=b'\x7fELF' else 'ELF'}
  for rel in ['boot.scr','boot.cmd','boot/e2e-003/boot.cmd']:
   p=boot/rel
   if p.is_file():
    b=p.read_bytes();out['files']['FAT/'+rel]={'sha256':hashlib.sha256(b).hexdigest(),'text':b.decode(errors='replace')[:16000]}
  out['init_scripts']=[p.name for p in (root/'etc/init.d').glob('*')]
  cfg=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-006/output/.config').read_text().splitlines()
  required=['CONFIG_VT=y','CONFIG_VT_CONSOLE=y','CONFIG_FRAMEBUFFER_CONSOLE=y','CONFIG_DRM=m','CONFIG_DRM_AMDGPU=m','CONFIG_DRM_FBDEV_EMULATION=y','CONFIG_FONT_8x16=y']
  out['candidate_console_config']={x:x in cfg for x in required};assert all(out['candidate_console_config'].values())
  (W/'boot-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='identity'},indent=2))
 finally:subprocess.run(['umount',str(boot)],check=True)
finally:subprocess.run(['umount',str(root)],check=True)
