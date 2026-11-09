from pathlib import Path
import subprocess,json,os,pwd
w=Path('/srv/data1/tabor-build/linux-live-001/work/mesa-3d-contracts-20261109-001');root=Path('/home/owner/offline-shader-spe-20261109-001/root');capture=w/'offline-spe-captures';capture.mkdir(exist_ok=False);owner=pwd.getpwnam('owner');os.chown(capture,owner.pw_uid,owner.pw_gid);os.chmod(root/'tmp',0o777)
shim=root/'usr/lib/libamdgpu_noop_drm_shim.so';assert shim.is_file()
base=['systemd-run','--quiet','--wait','--pipe','--collect','--property=User=owner','--property=Group=owner','--property=CPUQuota=100%','--property=MemoryMax=1G','--property=PrivateDevices=yes','--property=NoNewPrivileges=yes','--property=ProtectSystem=strict','--property=ReadWritePaths='+str(capture)+' '+str(root/'tmp'),'--unit=tabor-offline-spe-20261109-001','/usr/bin/timeout','45','/usr/bin/qemu-ppc','-cpu','e500v2','-L',str(root)]
env={'LD_PRELOAD':str(shim),'AMDGPU_GPU_ID':'polaris12','DRM_SHIM_DEBUG':'1','MESA_LOADER_DRIVER_OVERRIDE':'radeonsi','GALLIUM_DRIVER':'radeonsi','PIGLIT_PLATFORM':'surfaceless_egl','EGL_PLATFORM':'surfaceless','LIBGL_DRIVERS_PATH':str(root/'usr/lib/dri'),'MESA_SHADER_CACHE_DISABLE':'true','TABOR_SHADER_CAPTURE_DIR':str(capture)}
for k,v in env.items():base+=['-E',k+'='+v]
base+=[str(root/'lib/ld.so.1'),'--library-path',str(root/'lib')+':'+str(root/'usr/lib')]
cmd=base+[str(root/'usr/bin/shader_runner_gles2'),str(root/'tests/glsl-no-vertex-attribs.shader_test'),'-auto','-fbo']
with (w/'offline-spe-point.log').open('wb') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=55)
(w/'offline-spe-run.json').write_text(json.dumps({'argv':cmd,'exit':r.returncode,'capture_files':[p.name for p in capture.iterdir()],'gpu_execution':False,'profile':'upstream Polaris12 no-op; not actual Polaris11 board acceptance','resource_policy':'systemd user owner,1CPU/1GiB,PrivateDevices,ProtectSystem strict'},indent=2)+'\n');print('offline SPE exit',r.returncode,'captured',len(list(capture.iterdir())));print((w/'offline-spe-point.log').read_text(errors='replace')[-3000:])
