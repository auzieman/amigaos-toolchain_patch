import runpy,subprocess,pathlib,struct,zlib,json
b=runpy.run_path('tabor-spe-toolchain/work/modular-usb-update-20261105-001/board_access.py');ssh=b['ssh'];w=pathlib.Path('tabor-spe-toolchain/docs/builds/ib-fetch-contract-20261108')
ssh('set -e; mount -o remount,rw /; mkdir -p /mnt/usb-boot; mount -t vfat /dev/sdb1 /mnt/usb-boot',timeout=15)
s=ssh('cat /mnt/usb-boot/boot-010.scr',capture_output=True,timeout=15).stdout
h=bytearray(s[:64]);magic,hcrc,_,size,_,_,crc=struct.unpack_from('>7I',h);h[4:8]=bytes(4)
assert magic==0x27051956 and zlib.crc32(h)==hcrc and len(s)==size+64 and zlib.crc32(s[64:])==crc
assert b'/boot/e2e-010/uImage' in s and b'root=PARTUUID=a1221108-02' in s
# Reverify all previously staged010 kernel/module bytes before selecting.
expected=(w/'stage-010-verification.txt').read_text();paths=[line.split(None,1)[1] for line in expected.splitlines()]
import shlex
r=ssh('/sbin/busybox-modules sha256sum '+' '.join(shlex.quote(x) for x in paths),capture_output=True,text=True,timeout=30)
assert dict(x.split(None,1) for x in r.stdout.splitlines())==dict(x.split(None,1) for x in expected.splitlines())
ssh('set -e; cp /mnt/usb-boot/boot.scr /mnt/usb-boot/boot-009-rollback.scr; cp /mnt/usb-boot/boot.cmd /mnt/usb-boot/boot-009-rollback.cmd; cp /mnt/usb-boot/boot-010.scr /mnt/usb-boot/boot.scr.new; sync; mv /mnt/usb-boot/boot.scr.new /mnt/usb-boot/boot.scr; cp /mnt/usb-boot/boot-010.cmd /mnt/usb-boot/boot.cmd; sync',timeout=20)
assert ssh('cat /mnt/usb-boot/boot.scr',capture_output=True,timeout=15).stdout==s
ssh('set -e; umount /mnt/usb-boot; mount -o remount,ro /; sync',timeout=20)
(w/'activation-010.json').write_text(json.dumps({'selected':'6.12.113-tabor-e2e-010','readback_verified':True,'rollback':'boot-009-rollback.scr','reboot_requested':True},indent=2)+'\n')
print('010 selected and verified;009 rollback retained; requesting direct reboot',flush=True)
try:ssh('reboot -f',timeout=12)
except (subprocess.TimeoutExpired,subprocess.CalledProcessError):print('Reboot SSH disconnected/timed out; awaiting startup',flush=True)
