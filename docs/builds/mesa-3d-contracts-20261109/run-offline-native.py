from pathlib import Path
import subprocess,json
w=Path('/srv/data1/tabor-build/linux-live-001/work/mesa-3d-contracts-20261109-001')
assert (w/'native/result.exit').read_text().strip()=='0'
image='sha256:92b850162c8dcc8aced3d4766e1da85d5b0a63cfcdb14c4732c0756c612d5eef'
cap=w/'offline-native-captures';cap.mkdir(exist_ok=True)
script="""set -eu
export LD_LIBRARY_PATH=/work/native/output/usr/lib
export LD_PRELOAD=/work/native/output/usr/lib/libamdgpu_noop_drm_shim.so
export AMDGPU_GPU_ID=polaris12 DRM_SHIM_DEBUG=1
export MESA_LOADER_DRIVER_OVERRIDE=radeonsi GALLIUM_DRIVER=radeonsi
export PIGLIT_PLATFORM=surfaceless_egl EGL_PLATFORM=surfaceless
export MESA_SHADER_CACHE_DISABLE=true TABOR_SHADER_CAPTURE_DIR=/work/offline-native-captures
exec timeout 35 /usr/lib/x86_64-linux-gnu/piglit/bin/shader_runner_gles2 /runtime/tests/glsl-no-vertex-attribs.shader_test -auto -fbo
"""
cmd=['docker','run','--rm','--cpus=2','--memory=2g','--network=none','-v',str(w)+':/work','-v','/home/owner/offline-shader-spe-20261109-001/root:/runtime:ro','--entrypoint','sh',image,'-c',script]
with (w/'offline-native-point.log').open('wb') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=45)
(w/'offline-native-run.json').write_text(json.dumps({'argv':cmd,'image':image,'exit':r.returncode,'gpu_execution':False,'capture_files':[p.name for p in cap.iterdir()]},indent=2)+'\n')
print((w/'offline-native-point.log').read_text()[-4000:]);print('captures',len(list(cap.iterdir())))
