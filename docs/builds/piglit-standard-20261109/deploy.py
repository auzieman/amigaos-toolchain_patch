import subprocess,runpy,json,shlex
from pathlib import Path
b=runpy.run_path('tabor-spe-toolchain/work/modular-usb-update-20261105-001/board_access.py')['base'];d=Path('tabor-spe-toolchain/docs/builds/piglit-standard-20261109');root='/opt/tabor-piglit-20261109'
def ssh(c,**kw):return subprocess.run(['ssh',*b,'root@192.168.1.249',c],**kw)
r=ssh('uname -r; cat /sys/module/amdgpu/parameters/polaris11_le_user_ib; cat /proc/sys/kernel/tainted; df -k /',capture_output=True,text=True,check=True,timeout=15);assert r.stdout.splitlines()[:3]==['6.12.113-tabor-e2e-013','Y','0'];(d/'deploy-preflight.txt').write_text(r.stdout)
w='/home/owner/piglit-standard-live-20261109-001'
r=subprocess.run(['python3','lab/consolidation-20261002/r730-prep-20261031/remote.py','cat '+w+'/receipt.json'],capture_output=True,check=True);receipt=json.loads(r.stdout);(d/'runtime-receipt.json').write_bytes(r.stdout)
a=subprocess.Popen(['python3','lab/consolidation-20261002/r730-prep-20261031/remote.py','cat '+w+'/runtime.tar'],stdout=subprocess.PIPE)
r=ssh('set -e; test ! -e '+root+'; mount -o remount,rw /; mkdir '+root+'; /sbin/busybox-modules tar -xf - -C '+root+'; sync; mount -o remount,ro /',stdin=a.stdout,capture_output=True,text=True,timeout=70);a.stdout.close();assert a.wait()==0;r.check_returncode()
# Verify each regular file from the assembly receipt on the target.
cmd='/sbin/busybox-modules sha256sum '+' '.join(shlex.quote(root+'/'+f) for f in receipt['files'])
r=ssh(cmd,capture_output=True,text=True,check=True,timeout=30)
for line in r.stdout.splitlines():
 h,p=line.split(None,1);assert receipt['files'][p.removeprefix(root+'/')]==h,p
(d/'runtime-readback.txt').write_text(r.stdout)
# Mount only runtime interfaces needed by the private test chroot.
r=ssh('set -e; '+ '; '.join('mount -o bind /'+v+' '+root+'/'+v for v in ['dev','proc','sys','run'])+'; cat /proc/mounts',capture_output=True,text=True,check=True,timeout=20)
assert any(x.split()[1]=='/' and 'ro' in x.split()[3].split(',') for x in r.stdout.splitlines());(d/'runtime-mounts.txt').write_text(r.stdout)
print('Private runtime installed; all file hashes match; root read-only; interfaces mounted.')
