"""One authorized standard offscreen RGB trial; no scanout/VT/reload/reset changes."""
from pathlib import Path
import subprocess,runpy,json,time,os,signal
repo=Path(__file__).resolve().parents[4]
b=runpy.run_path(str(repo/'work/modular-usb-update-20261105-001/board_access.py'))['base']
d=Path(__file__).resolve().parent/'physical-rgb-014-001';d.mkdir(exist_ok=False)
root='/opt/tabor-native-vertex-20261109'
def ssh(cmd,timeout=15):return subprocess.run(['ssh',*b,'root@192.168.1.249',cmd],capture_output=True,text=True,timeout=timeout)
def get(cmd):
 r=ssh(cmd);assert r.returncode==0,r.stderr;return r.stdout
pre=get('uname -r; cat /proc/sys/kernel/tainted; cat /sys/module/amdgpu/parameters/polaris11_le_user_ib; cat /proc/sys/kernel/random/boot_id; mount')
(d/'preflight.txt').write_text(pre);assert pre.splitlines()[:3]==['6.12.113-tabor-e2e-014','0','Y'];assert '/dev/root on / type ext4 (ro,' in pre
before=get('dmesg');(d/'before-kmsg.txt').write_text(before)
assert not any(s in before.lower() for s in ['gpu reset','blocked for more than','ring gfx_0.0.0 timeout','ring gfx timeout'])
expected=json.loads((d.parent.parent/'staging/runtime-receipt.json').read_text())['files']['usr/lib/libgallium-25.0.7.so']
assert get('/sbin/busybox-modules sha256sum '+root+'/usr/lib/libgallium-25.0.7.so').split()[0]==expected
mounts=get('mount');assert root+'/dev ' not in mounts
get('set -e; '+'; '.join('mount -o bind /'+n+' '+root+'/'+n for n in ['dev','proc','sys','run']))
(d/'mounted-interfaces.txt').write_text(get('mount'))
baseenv='PIGLIT_PLATFORM=surfaceless_egl EGL_PLATFORM=surfaceless MESA_SHADER_CACHE_DISABLE=true TABOR_POLARIS11_LE_IB=1 TABOR_NATIVE_VERTEX_DATA=1 LIBGL_ALWAYS_SOFTWARE=0 GALLIUM_DRIVER=radeonsi MESA_LOADER_DRIVER_OVERRIDE=radeonsi '
results=[]
with (d/'live-kmsg.txt').open('wb') as f,(d/'live-kmsg.stderr').open('wb') as err:
 log=subprocess.Popen(['ssh',*b,'root@192.168.1.249','cat /dev/kmsg'],stdout=f,stderr=err,start_new_session=True)
 try:
  get('echo TABOR_NATIVE_VERTEX_RGB_BEGIN > /dev/kmsg');time.sleep(.3)
  assert log.poll() is None and b'TABOR_NATIVE_VERTEX_RGB_BEGIN' in (d/'live-kmsg.txt').read_bytes()
  assert get('cat /sys/module/amdgpu/parameters/polaris11_submit_trace').strip()=='N'
  get('echo 1 > /sys/module/amdgpu/parameters/polaris11_submit_trace')
  # Reuse verified query binary with the NEW loader/libraries, no draw/scanout.
  cmd=baseenv+'LD_LIBRARY_PATH='+root+'/lib:'+root+'/usr/lib '+root+'/lib/ld.so.1 --library-path '+root+'/lib:'+root+'/usr/lib /opt/tabor-piglit-20261109/usr/bin/wflinfo --platform=surfaceless_egl --api=gles2'
  r=ssh(cmd,20);out=r.stdout+r.stderr;(d/'renderer.txt').write_text(out)
  assert r.returncode==0 and 'radeonsi' in out.lower() and 'polaris11' in out.lower(),out
  print(out[-900:],flush=True)
  cmd=baseenv+'LD_LIBRARY_PATH=/lib:/usr/lib /run/busybox-render-tools timeout 12 /run/busybox-render-tools chroot '+root+' /usr/bin/shader_runner_gles2 /tests/sanity.shader_test -auto -fbo'
  print('Starting single standard RGB FBO trial',flush=True)
  try:
   r=ssh(cmd,22);out=r.stdout+r.stderr
   result={'exit':r.returncode,'pass':r.returncode==0 and '"result": "pass"' in out,'controller_timeout':False,'command':cmd}
  except subprocess.TimeoutExpired as e:
   out=e.stdout or b'';out=out.decode(errors='replace') if isinstance(out,bytes) else out
   partial_err=e.stderr or b''
   out+=partial_err.decode(errors='replace') if isinstance(partial_err,bytes) else partial_err
   result={'exit':None,'pass':False,'controller_timeout':True,'command':cmd};out+='\nCONTROLLER_TIMEOUT; NO RETRY/RESET\n'
  (d/'rgb-result.txt').write_text(out);(d/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(out[-1800:],flush=True)
  try:
   r=ssh('cat /proc/sys/kernel/tainted; cat /proc/sys/kernel/random/boot_id; cat /proc/fb; mount; dmesg',12)
   (d/'after-state.txt').write_text(r.stdout+r.stderr)
  except subprocess.TimeoutExpired:(d/'after-state.txt').write_text('SSH status capture timed out; no further workload.\n')
  # Retain automatic watchdog messages if failed; no manual recovery action.
  if not result['pass']:time.sleep(12)
 finally:
  if log.poll() is None:
   os.killpg(log.pid,signal.SIGTERM)
   try:log.wait(timeout=3)
   except subprocess.TimeoutExpired:os.killpg(log.pid,signal.SIGKILL);log.wait()
print('Trial complete; no second graphics workload, reset, reload, VT switch or reboot.')
