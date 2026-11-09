import subprocess,runpy,time
from pathlib import Path
b=runpy.run_path('tabor-spe-toolchain/work/modular-usb-update-20261105-001/board_access.py')['base'];d=Path('tabor-spe-toolchain/docs/builds/radeonsi-aco-20261109')
def ssh(c,**kw):return subprocess.run(['ssh',*b,'root@192.168.1.249',c],**kw)
with (d/'physical-kmsg.txt').open('w') as f:
 log=subprocess.Popen(['ssh',*b,'root@192.168.1.249','cat /dev/kmsg'],stdout=f,stderr=subprocess.STDOUT)
 try:
  time.sleep(1)
  assert log.poll() is None
  ssh('echo TABOR_ACO_FIRST_FRAME_BEGIN > /dev/kmsg',check=True)
  time.sleep(1);assert 'TABOR_ACO_FIRST_FRAME_BEGIN' in (d/'physical-kmsg.txt').read_text()
  script='''#!/bin/sh
trap '/run/busybox-render-tools chvt 1' EXIT
/run/busybox-render-tools chvt 2 || exit 2
MESA_LOADER_DRIVER_OVERRIDE=radeonsi GALLIUM_DRIVER=radeonsi LIBGL_DRIVERS_PATH=/usr/lib/dri LD_LIBRARY_PATH=/lib:/usr/lib MESA_SHADER_CACHE_DISABLE=true EGL_LOG_LEVEL=debug TABOR_REQUIRE_HARDWARE=1 TABOR_READBACK=1 /run/busybox-render-tools timeout 60 /run/busybox-render-tools chroot /opt/tabor-radeonsi-20261109 /usr/bin/kmscube -D /dev/dri/card0 -m 0 -c 1 > /run/kmscube-hardware.log 2>&1
r=$?
echo "$r" > /run/kmscube-hardware.exit
echo TABOR_ACO_FIRST_FRAME_END > /dev/kmsg
exit "$r"
'''
  ssh('cat > /run/run-hardware.sh',input=script,text=True,check=True)
  r=ssh('/run/busybox-render-tools setsid sh /run/run-hardware.sh < /dev/null',capture_output=True,text=True,timeout=80)
  (d/'physical-invoke.txt').write_text(str(r.returncode)+'\n'+r.stdout+r.stderr)
  r=ssh('cat /run/kmscube-hardware.exit /run/kmscube-hardware.log; cat /proc/sys/kernel/tainted; cat /sys/class/tty/tty0/active',capture_output=True,text=True,timeout=15)
  (d/'physical-result.txt').write_text(r.stdout+r.stderr);print(r.stdout,r.stderr)
 finally:
  log.terminate()
  try:log.wait(timeout=5)
  except subprocess.TimeoutExpired:log.kill()
