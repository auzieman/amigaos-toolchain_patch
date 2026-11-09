from pathlib import Path
import subprocess,json
b=Path('/srv/data1/tabor-build/linux-live-001');w=b/'work/piglit-standard-20261109-001';parent=b/'work/radeonsi-systemic-20261109-001'
subprocess.run(['cp','-a','--reflink=auto',str(parent/'stage'),str(w/'stage')],check=True)
subprocess.run(['cp','-a',str(parent/'output')+'/.',str(w/'stage')],check=True)
s=(parent/'spe-cross.ini').read_text().replace('/work/radeonsi-aco-20261109-001','/work/piglit');(w/'spe-cross.ini').write_text(s)
(w/'toolchain.cmake').write_text('''set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR powerpc)
set(CMAKE_C_COMPILER /tools/bin/powerpc-linux-gnuspe-gcc)
set(CMAKE_CXX_COMPILER /tools/bin/powerpc-linux-gnuspe-g++)
set(CMAKE_SYSROOT /sysroot)
set(CMAKE_FIND_ROOT_PATH /work/piglit/stage /sysroot)
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)
set(CMAKE_C_FLAGS_INIT "-mcpu=8548 -mabi=spe -mspe -mfloat-gprs=double -mlong-double-128 -I/work/piglit/stage/usr/include")
set(CMAKE_CXX_FLAGS_INIT "-mcpu=8548 -mabi=spe -mspe -mfloat-gprs=double -mlong-double-128 -I/work/piglit/stage/usr/include")
set(CMAKE_EXE_LINKER_FLAGS_INIT "-L/work/piglit/stage/usr/lib -L/work/piglit/stage/usr/lib/powerpc-linux-gnuspe -Wl,-rpath-link,/work/piglit/stage/usr/lib -Wl,-rpath-link,/work/piglit/stage/usr/lib/powerpc-linux-gnuspe")
''')
script='''set -e
w=/work/piglit
meson setup "$w/waffle-build" "$w/waffle" --cross-file "$w/spe-cross.ini" --prefix=/usr --libdir=lib --wrap-mode=nodownload -Dglx=disabled -Dx11_egl=disabled -Dwayland=disabled -Dgbm=enabled -Dsurfaceless_egl=enabled -Dbuild-tests=false -Dbuild-examples=false > "$w/waffle-configure.log" 2>&1
ninja -C "$w/waffle-build" -j2 > "$w/waffle-build.log" 2>&1
DESTDIR="$w/stage" ninja -C "$w/waffle-build" install > "$w/waffle-install.log" 2>&1
export PKG_CONFIG_LIBDIR="$w/stage/usr/lib/pkgconfig:$w/stage/usr/lib/powerpc-linux-gnuspe/pkgconfig"
export PKG_CONFIG_SYSROOT_DIR="$w/stage"
cmake -S "$w/piglit" -B "$w/piglit-build" -G Ninja -DCMAKE_TOOLCHAIN_FILE="$w/toolchain.cmake" -DCMAKE_BUILD_TYPE=Release -DPIGLIT_USE_WAFFLE=ON -DPIGLIT_USE_X11=OFF -DPIGLIT_USE_WAYLAND=OFF -DPIGLIT_USE_GBM=ON -DPIGLIT_BUILD_GL_TESTS=OFF -DPIGLIT_BUILD_GLES1_TESTS=OFF -DPIGLIT_BUILD_GLES2_TESTS=ON -DPIGLIT_BUILD_GLES3_TESTS=OFF -DPIGLIT_BUILD_GLX_TESTS=OFF -DPIGLIT_BUILD_EGL_TESTS=ON -DPIGLIT_BUILD_DMA_BUF_TESTS=OFF -DPIGLIT_BUILD_VK_TESTS=OFF -DPIGLIT_BUILD_CL_TESTS=OFF > "$w/piglit-configure.log" 2>&1
ninja -C "$w/piglit-build" -j2 shader_runner_gles2 minmax_gles2 glsl-fs-pointcoord_gles2 > "$w/piglit-build.log" 2>&1
'''
script='trap \'r=$?; echo "$r" > /work/piglit/result.exit\' EXIT\n'+script
cmd=['docker','run','-d','--name','tabor-piglit-standard-20261109-001','--cpus=2','--memory=4g','--network=none','-v',str(w)+':/work/piglit','-v',str(b/'tools/cxx-reference-002')+':/tools:ro','-v',str(b/'sysroot')+':/sysroot:ro','--entrypoint','sh','sha256:0434a7f8dfeec379cd81d334e2a2eaa02208653e494d56334bcc486950be8a49','-c',script]
r=subprocess.run(cmd,capture_output=True,text=True);(w/'launch.json').write_text(json.dumps({'argv':cmd,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n');print(r.stdout,r.stderr);r.check_returncode()
