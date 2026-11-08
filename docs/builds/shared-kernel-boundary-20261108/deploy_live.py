"""Install the verified complete kernel set over SSH; retain e2e-001 rollback."""
from pathlib import Path
import subprocess,runpy,json,hashlib,shlex,struct,zlib
D=Path(__file__).resolve().parent;R=D.parents[2]
base=runpy.run_path(str(R/'work/modular-usb-update-20261105-001/board_access.py'))['base']
ssh=['flatpak-spawn','--host','ssh',*base,'root@192.168.1.249']
remote='/home/auzieman/Projects/lab/consolidation-20261002/r730-prep-20261031/remote.py'
receipt=json.loads((D/'receipt-e2e002.json').read_text());rel=receipt['kernel_release'];q=shlex.quote
stage='/run/tabor-update-002';boot='/mnt/tabor-update-boot'
result={'status':'started','release':rel,'gpu_loaded':False,'rebooted':False,'old_kernel_retained':True}
def run(cmd,data=None):
 r=subprocess.run(ssh+[cmd],input=data,capture_output=True,timeout=90)
 if r.returncode:raise RuntimeError(cmd[:90]+' '+r.stderr.decode(errors='replace'))
 return r.stdout
def fetch(path):
 r=subprocess.run(['python3',remote,'cat '+q(path)],capture_output=True,timeout=90,check=True);return r.stdout
def sha(data):return hashlib.sha256(data).hexdigest()
def check(path,digest):
 assert run('/sbin/busybox-modules sha256sum '+q(path)).decode().split()[0]==digest,path
mounted=False
try:
 pre=run('uname -r; cat /proc/modules; cat /proc/mounts');(D/'deploy-preflight.txt').write_bytes(pre)
 assert pre.splitlines()[0]==b'6.12.113-tabor-e2e-001'
 assert not any(l.startswith(b'amdgpu ') for l in pre.splitlines())
 assert run('cat /sys/bus/usb/devices/1-1.4/serial').decode().strip()=='03001919041721081205'
 run('test ! -e /lib/modules/'+rel+' && test ! -e '+stage)
 archive=fetch('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-002/update.tar')
 assert sha(archive)==receipt['tar_sha256']
 script=fetch('/home/owner/shared-boundary-20261108/boot-e2e002.scr')
 magic,hcrc,_,size,_,_,dcrc=struct.unpack_from('>7I',script);hdr=bytearray(script[:64]);hdr[4:8]=b'\0'*4
 assert magic==0x27051956 and len(script)==size+64 and zlib.crc32(hdr)==hcrc and zlib.crc32(script[64:])==dcrc
 assert script[72:]==(D/'boot-e2e002.cmd').read_bytes()
 run('mkdir -p '+stage+' && mount -t tmpfs -o size=64m,mode=700 tmpfs '+stage)
 run('cat > '+stage+'/update.tar',archive);check(stage+'/update.tar',receipt['tar_sha256'])
 run('/bin/busybox tar xf '+stage+'/update.tar -C '+stage)
 for name,digest in receipt['bundle_files_sha256'].items():check(stage+'/'+name,digest)
 run('mkdir -p '+boot+' && mount -t vfat /dev/sdb1 '+boot);mounted=True
 check(boot+'/boot.scr','dff9c8cd31184e872f2c49b2da8255c58160f32fdc7f02d74b844357365e677d')
 oldscript=run('cat '+boot+'/boot.scr');(D/'rollback-e2e001.scr').write_bytes(oldscript)
 # Install only a new module-release directory. Existing firmware is verified,
 # never replaced (its known bytes and alias relationships remain intact).
 for name,digest in receipt['bundle_files_sha256'].items():
  if name.startswith('root/lib/firmware/'):check('/'+name[5:],digest)
 run('cp -a '+stage+'/root/lib/modules/'+rel+' /lib/modules/')
 for name,digest in receipt['bundle_files_sha256'].items():
  if name.startswith('root/lib/modules/'):check('/'+name[5:],digest)
 run('test ! -e '+boot+'/boot/e2e-002 && mkdir -p '+boot+'/boot/e2e-002 && cp '+stage+'/fat/boot/e2e/uImage '+boot+'/boot/e2e-002/uImage && cp '+stage+'/fat/boot/e2e/tabor.dtb '+boot+'/boot/e2e-002/tabor.dtb')
 for name in ['uImage','tabor.dtb']:check(boot+'/boot/e2e-002/'+name,receipt['bundle_files_sha256']['fat/boot/e2e/'+name])
 run('cat > '+boot+'/boot-e2e002.scr',script);check(boot+'/boot-e2e002.scr',sha(script))
 run('cat > '+boot+'/boot-e2e001-rollback.scr',oldscript);check(boot+'/boot-e2e001-rollback.scr',sha(oldscript))
 run('cat > '+boot+'/boot.scr.next',script);check(boot+'/boot.scr.next',sha(script))
 run('sync && mv '+boot+'/boot.scr.next '+boot+'/boot.scr && sync');check(boot+'/boot.scr',sha(script))
 result.update(status='installed-and-selected-awaiting-reboot',boot_script_sha256=sha(script),rollback_script_sha256=sha(oldscript),module_sha256=receipt['module_verification']['module_sha256'])
except Exception as exc:result.update(status='incomplete',error=str(exc));raise
finally:
 if mounted:run('sync && umount '+boot)
 (D/'live-deploy.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
