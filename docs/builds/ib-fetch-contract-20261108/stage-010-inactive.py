import subprocess,runpy,pathlib,json,tarfile,io,struct,zlib
base=runpy.run_path('tabor-spe-toolchain/work/modular-usb-update-20261105-001/board_access.py')['base']
def ssh(c,**kw):return subprocess.run(['ssh',*base,'root@192.168.1.249',c],check=True,**kw)
w=pathlib.Path('tabor-spe-toolchain/docs/builds/ib-fetch-contract-20261108'); r=json.loads((w/'build-010-receipt.json').read_text())
p=pathlib.Path('/tmp/tabor010-update.tar')
with p.open('wb') as f:subprocess.run(['python3','lab/consolidation-20261002/r730-prep-20261031/remote.py','cat /srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-010/update.tar'],stdout=f,check=True)
ssh('set -e; test "$(uname -r)" = 6.12.113-tabor-e2e-009; mount -o remount,rw /; mkdir -p /mnt/usb-boot; mount -t vfat /dev/sdb1 /mnt/usb-boot; test -f /mnt/usb-boot/boot/e2e-009/uImage; cat /mnt/usb-boot/boot.cmd',stdout=(w/'previous-boot-009.cmd').open('w'))
old=(w/'previous-boot-009.cmd').read_text();assert 'e2e-009' in old and 'a1221108-02' in old
cmd=old.replace('009','010').encode(); name=b'Tabor console 010'; h=struct.pack('>7I4B32s',0x27051956,0,0,len(cmd),0,0,zlib.crc32(cmd),5,7,6,0,name);h=bytearray(h);struct.pack_into('>I',h,4,zlib.crc32(h));script=bytes(h)+cmd
# U-Boot script images require a big-endian length table preceding script text.
payload=struct.pack('>II',len(cmd),0)+cmd
h=bytearray(struct.pack('>7I4B32s',0x27051956,0,0,len(payload),0,0,zlib.crc32(payload),5,7,6,0,name));struct.pack_into('>I',h,4,zlib.crc32(h));script=bytes(h)+payload
checks=[]
with tarfile.open(p) as src:
 proc=subprocess.Popen(['ssh',*base,'root@192.168.1.249','tar xf - -C /'],stdin=subprocess.PIPE)
 with tarfile.open(fileobj=proc.stdin,mode='w|') as dst:
  for m in src:
   if not m.isfile():continue
   if m.name.startswith('root/lib/modules/6.12.113-tabor-e2e-010/'):
    target=m.name[5:]
   elif m.name.startswith('fat/boot/e2e/'):
    target='mnt/usb-boot/boot/e2e-010/'+m.name.split('fat/boot/e2e/',1)[1]
   else:continue
   data=src.extractfile(m).read();import hashlib
   assert hashlib.sha256(data).hexdigest()==r['bundle_files_sha256'][m.name]
   checks.append(hashlib.sha256(data).hexdigest()+'  /'+target)
   m.name=target;dst.addfile(m,io.BytesIO(data))
  for target,data in [('run/010-checks.sha256',('\n'.join(checks)+'\n').encode()),('mnt/usb-boot/boot-010.cmd',cmd),('mnt/usb-boot/boot-010.scr',script)]:
   t=tarfile.TarInfo(target);t.size=len(data);t.mode=0o644;dst.addfile(t,io.BytesIO(data))
 proc.stdin.close();assert proc.wait()==0

a=ssh('while read expected file; do /sbin/busybox-modules sha256sum "$file"; done < /run/010-checks.sha256',capture_output=True,text=True)
b=ssh('cat /run/010-checks.sha256',capture_output=True,text=True)
assert dict(x.split(None,1) for x in a.stdout.splitlines())==dict(x.split(None,1) for x in b.stdout.splitlines())
(w/'stage-010-verification.txt').write_text(a.stdout)
assert ssh('cat /mnt/usb-boot/boot-010.scr',capture_output=True).stdout==script
# Preserve the selected009 script byte-for-byte. No active boot-default change.
assert ssh('cat /mnt/usb-boot/boot.cmd',capture_output=True,text=True).stdout==old
ssh('set -e; sync; umount /mnt/usb-boot; mount -o remount,ro /; sync')
print('010 staged inactive and all hashes verified. 009 remains selected. No reboot.')
