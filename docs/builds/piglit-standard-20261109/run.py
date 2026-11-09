import subprocess,runpy,time,json
from pathlib import Path
b=runpy.run_path('tabor-spe-toolchain/work/modular-usb-update-20261105-001/board_access.py')['base'];d=Path('tabor-spe-toolchain/docs/builds/piglit-standard-20261109');root='/opt/tabor-piglit-20261109'
def ssh(c,**kw):return subprocess.run(['ssh',*b,'root@192.168.1.249',c],**kw)
src='/srv/data1/tabor-build/linux-live-001/work/piglit-standard-20261109-001/waffle-build/src/utils/wflinfo'
a=subprocess.Popen(['python3','lab/consolidation-20261002/r730-prep-20261031/remote.py','cat '+src],stdout=subprocess.PIPE)
r=ssh('set -e; mount -o remount,rw /; cat > '+root+'/usr/bin/wflinfo; chmod 755 '+root+'/usr/bin/wflinfo; sync; mount -o remount,ro /; /sbin/busybox-modules sha256sum '+root+'/usr/bin/wflinfo',stdin=a.stdout,capture_output=True,text=True,timeout=20);a.stdout.close();assert a.wait()==0;r.check_returncode()
h=subprocess.check_output(['python3','lab/consolidation-20261002/r730-prep-20261031/remote.py','sha256sum '+src],text=True).split()[0];assert r.stdout.split()[0]==h;(d/'wflinfo-readback.txt').write_text(r.stdout)
r=ssh('uname -r; cat /sys/module/amdgpu/parameters/polaris11_le_user_ib; cat /proc/sys/kernel/tainted',capture_output=True,text=True,check=True,timeout=15);assert r.stdout.splitlines()==['6.12.113-tabor-e2e-013','Y','0']
results=[]
with (d/'physical-kmsg.txt').open('w') as f:
 log=subprocess.Popen(['ssh',*b,'root@192.168.1.249','cat /dev/kmsg'],stdout=f,stderr=subprocess.STDOUT)
 try:
  time.sleep(1);assert log.poll() is None
  ssh('echo TABOR_STANDARD_PIGLIT_BEGIN > /dev/kmsg',check=True);time.sleep(.5);assert 'TABOR_STANDARD_PIGLIT_BEGIN' in (d/'physical-kmsg.txt').read_text()
  for backend in ['softpipe','radeonsi']:
   env='PIGLIT_PLATFORM=surfaceless_egl EGL_PLATFORM=surfaceless LD_LIBRARY_PATH=/lib:/usr/lib LIBGL_DRIVERS_PATH=/usr/lib/dri MESA_SHADER_CACHE_DISABLE=true TABOR_POLARIS11_LE_IB=1 '
   env+=('LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=softpipe MESA_LOADER_DRIVER_OVERRIDE=swrast ' if backend=='softpipe' else 'LIBGL_ALWAYS_SOFTWARE=0 GALLIUM_DRIVER=radeonsi MESA_LOADER_DRIVER_OVERRIDE=radeonsi ')
   commands=[('renderer','/usr/bin/wflinfo --platform=surfaceless_egl --api=gles2'),('minmax','/usr/bin/minmax_gles2 -auto -fbo'),('point-no-attributes','/usr/bin/shader_runner_gles2 /tests/glsl-no-vertex-attribs.shader_test -auto -fbo'),('sanity-rgb','/usr/bin/shader_runner_gles2 /tests/sanity.shader_test -auto -fbo')]
   for name,cmd in commands:
    print(backend,name,flush=True)
    try:
     r=ssh(env+'/run/busybox-render-tools timeout 30 /run/busybox-render-tools chroot '+root+' '+cmd,capture_output=True,text=True,timeout=40)
    except subprocess.TimeoutExpired as exc:
     out=exc.stdout or b''
     if isinstance(out,bytes):out=out.decode(errors='replace')
     (d/(backend+'-'+name+'.txt')).write_text(out+'\nCONTROLLER_TIMEOUT_40S\n')
     results.append({'backend':backend,'test':name,'exit':None,'status':'controller-timeout-40s','piglit_pass':False})
     (d/'results.json').write_text(json.dumps(results,indent=2)+'\n')
     raise RuntimeError('GPU test timed out; retain offboard log and stop hardware tests') from exc
    out=r.stdout+r.stderr;(d/(backend+'-'+name+'.txt')).write_text(out)
    item={'backend':backend,'test':name,'exit':r.returncode,'piglit_pass':"'result': 'pass'" in out or '"result": "pass"' in out};results.append(item);(d/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    print(out[-1800:],flush=True)
    assert r.returncode not in [124,137,255], 'timeout or SSH loss; stop'
    if name=='renderer':
     assert r.returncode==0,out
     assert ('softpipe' in out if backend=='softpipe' else 'radeonsi' in out and 'polaris11' in out),out
    health=ssh('cat /proc/sys/kernel/tainted',capture_output=True,text=True,check=True,timeout=10);assert health.stdout.strip()=='0'
  ssh('echo TABOR_STANDARD_PIGLIT_END > /dev/kmsg',check=True)
 finally:
  log.terminate()
  try:log.wait(timeout=5)
  except subprocess.TimeoutExpired:log.kill()
