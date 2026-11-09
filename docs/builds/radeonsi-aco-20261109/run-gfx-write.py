import subprocess,runpy,time,hashlib
from pathlib import Path
b=runpy.run_path('tabor-spe-toolchain/work/modular-usb-update-20261105-001/board_access.py')['base'];d=Path('tabor-spe-toolchain/docs/builds/radeonsi-aco-20261109')
def ssh(c,**kw):return subprocess.run(['ssh',*b,'root@192.168.1.249',c],**kw)
src='/srv/data1/tabor-build/linux-live-001/work/gfx-write-20261109-001/gfx-write';a=subprocess.Popen(['python3','lab/consolidation-20261002/r730-prep-20261031/remote.py','cat '+src],stdout=subprocess.PIPE)
r=ssh('cat > /run/gfx-write; chmod 755 /run/gfx-write; /sbin/busybox-modules sha256sum /run/gfx-write',stdin=a.stdout,capture_output=True,text=True);a.stdout.close();assert a.wait()==0;r.check_returncode();h=subprocess.check_output(['python3','lab/consolidation-20261002/r730-prep-20261031/remote.py','sha256sum '+src],text=True).split()[0];assert h==r.stdout.split()[0]
with (d/'gfx-write-kmsg.txt').open('w') as f:
 log=subprocess.Popen(['ssh',*b,'root@192.168.1.249','cat /dev/kmsg'],stdout=f,stderr=subprocess.STDOUT)
 try:
  time.sleep(1);assert log.poll() is None
  ssh('echo TABOR_GFX_NATIVE_WRITE_BEGIN > /dev/kmsg',check=True);time.sleep(1);assert 'TABOR_GFX_NATIVE_WRITE_BEGIN' in (d/'gfx-write-kmsg.txt').read_text()
  cmd='/run/busybox-render-tools timeout 10 /opt/tabor-radeonsi-20261109/lib/ld.so.1 --library-path /opt/tabor-radeonsi-20261109/lib:/opt/tabor-radeonsi-20261109/usr/lib /run/gfx-write; r=$?; echo GFX_WRITE_EXIT=$r; echo TABOR_GFX_NATIVE_WRITE_END > /dev/kmsg; cat /proc/sys/kernel/tainted'
  r=ssh(cmd,capture_output=True,text=True,timeout=20);(d/'gfx-write-result.txt').write_text(r.stdout+r.stderr);print(r.stdout,r.stderr)
 finally:
  log.terminate()
  try:log.wait(timeout=5)
  except subprocess.TimeoutExpired:log.kill()
