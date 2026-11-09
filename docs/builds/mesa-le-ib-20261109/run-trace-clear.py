import subprocess,runpy,time
from pathlib import Path
b=runpy.run_path('tabor-spe-toolchain/work/modular-usb-update-20261105-001/board_access.py')['base'];d=Path('tabor-spe-toolchain/docs/builds/mesa-le-ib-20261109')
def ssh(c,**kw):return subprocess.run(['ssh',*b,'root@192.168.1.249',c],**kw)
r=ssh('uname -r; cat /sys/module/amdgpu/parameters/polaris11_le_user_ib; cat /proc/sys/kernel/tainted',capture_output=True,text=True,check=True)
assert r.stdout.splitlines()==['6.12.113-tabor-e2e-013','Y','0']
with (d/'trace-clear-kmsg.txt').open('w') as f:
 log=subprocess.Popen(['ssh',*b,'root@192.168.1.249','cat /dev/kmsg'],stdout=f,stderr=subprocess.STDOUT)
 try:
  time.sleep(1)
  assert log.poll() is None
  ssh('echo TABOR_MESA_LE_TRACE_CLEAR_BEGIN > /dev/kmsg',check=True)
  time.sleep(1);assert 'TABOR_MESA_LE_TRACE_CLEAR_BEGIN' in (d/'trace-clear-kmsg.txt').read_text()
  script='''#!/bin/sh
trap '/run/busybox-render-tools chvt 1' EXIT
/run/busybox-render-tools chvt 2 || exit 2
TABOR_POLARIS11_LE_IB=1 MESA_LOADER_DRIVER_OVERRIDE=radeonsi GALLIUM_DRIVER=radeonsi LIBGL_DRIVERS_PATH=/usr/lib/dri LD_LIBRARY_PATH=/lib:/usr/lib MESA_SHADER_CACHE_DISABLE=true EGL_LOG_LEVEL=debug TABOR_REQUIRE_HARDWARE=1 TABOR_CLEAR_ONLY=1 TABOR_RENDER_ONLY=1 TABOR_READBACK=1 /run/busybox-render-tools timeout 60 /run/busybox-render-tools chroot /opt/tabor-mesa-le-ib-20261109 /usr/bin/kmscube -D /dev/dri/card0 -c 1 > /run/kmscube-hardware.log 2>&1
r=$?
echo "$r" > /run/kmscube-hardware.exit
echo TABOR_MESA_LE_TRACE_CLEAR_END > /dev/kmsg
exit "$r"
'''
  ssh('cat > /run/run-hardware.sh',input=script,text=True,check=True)
  r=ssh('/run/busybox-render-tools setsid sh /run/run-hardware.sh < /dev/null',capture_output=True,text=True,timeout=80)
  (d/'trace-clear-invoke.txt').write_text(str(r.returncode)+'\n'+r.stdout+r.stderr)
  r=ssh('cat /run/kmscube-hardware.exit /run/kmscube-hardware.log; cat /proc/sys/kernel/tainted; cat /sys/class/tty/tty0/active',capture_output=True,text=True,timeout=15)
  (d/'trace-clear-result.txt').write_text(r.stdout+r.stderr);print('\n'.join(x for x in (r.stdout+r.stderr).splitlines() if x.startswith(('TABOR_', '0', '255', 'tty')) or 'renderer:' in x))
 finally:
  log.terminate()
  try:log.wait(timeout=5)
  except subprocess.TimeoutExpired:log.kill()
