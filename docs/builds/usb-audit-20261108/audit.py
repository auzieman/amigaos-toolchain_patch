from pathlib import Path
import subprocess,json,hashlib
w=Path('/srv/data1/tabor-build/source-review/usb-audit-20261108');w.mkdir(exist_ok=True)
identity=json.loads(subprocess.check_output(['lsblk','--tree','-J','-o','NAME,PATH,SERIAL,TRAN,PARTUUID,MOUNTPOINTS','/dev/sde'],text=True))['blockdevices'][0]
assert identity['serial']=='03001919041721081205' and identity['tran']=='usb'
assert identity['children'][1]['partuuid']=='a1221105-02'
for child in identity['children']:assert not any(child['mountpoints'])
checks={}
for name,cmd in [('root',['e2fsck','-fn','/dev/sde2']),('fat',['fsck.fat','-n','/dev/sde1'])]:
 r=subprocess.run(cmd,capture_output=True,text=True);(w/(name+'-fsck.txt')).write_text(r.stdout+r.stderr);checks[name]=r.returncode
 assert r.returncode==0,(name,r.returncode)
root=Path('/mnt/tabor-audit-root');boot=Path('/mnt/tabor-audit-boot')
for p in [root,boot]:p.mkdir(exist_ok=True)
subprocess.run(['mount','-o','ro,noload','/dev/sde2',str(root)],check=True)
try:
 subprocess.run(['mount','-o','ro','/dev/sde1',str(boot)],check=True)
 try:
  sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
  files={'boot.scr':sha(boot/'boot.scr'),'uImage':sha(boot/'boot/e2e-003/uImage'),'module':sha(root/'lib/modules/6.12.113-tabor-e2e-003/kernel/drivers/gpu/drm/amd/amdgpu/amdgpu.ko')}
  found=[]
  for location in [root/'root',root/'var/log',root/'tmp']:
   if not location.exists():continue
   for p in location.rglob('*'):
    if p.is_file() and (p.suffix.lower() in ['.rom','.trace'] or 'vbios' in p.name.lower()):found.append({'path':str(p.relative_to(root)),'bytes':p.stat().st_size})
  report={'read_only':True,'journal_replay_disabled':True,'filesystem_checks':checks,'files_sha256':files,'retained_rom_or_trace_files':found,'boot_changed':False}
  (w/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
 finally:subprocess.run(['umount',str(boot)],check=True)
finally:subprocess.run(['umount',str(root)],check=True)
