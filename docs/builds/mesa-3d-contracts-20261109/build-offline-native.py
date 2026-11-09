from pathlib import Path
import subprocess,json
b=Path('/srv/data1/tabor-build/linux-live-001');w=b/'work/mesa-3d-contracts-20261109-001';(w/'native').mkdir(exist_ok=False);cache=b/'native-qualification-apt-cache';cache.mkdir(exist_ok=True)
script='''set -e
w=/work
trap 'r=$?; echo "$r" > "$w/native/result.exit"' EXIT
printf '%s\\n' 'deb [check-valid-until=no] https://snapshot.debian.org/archive/debian/20261102T220000Z/ trixie main' 'deb [check-valid-until=no] https://snapshot.debian.org/archive/debian-security/20261102T220000Z/ trixie-security main' > /etc/apt/sources.list
rm -f /etc/apt/sources.list.d/debian.sources
apt-get -o Acquire::Retries=3 -o Acquire::https::Timeout=30 update > "$w/native/apt-update.log" 2>&1
apt-get -y --no-install-recommends -o Acquire::Retries=3 install libdrm-dev libelf-dev libexpat1-dev zlib1g-dev piglit waffle-utils > "$w/native/apt-install.log" 2>&1
dpkg-query -W libc6 libdrm-dev libelf-dev libexpat1-dev zlib1g-dev piglit waffle-utils > "$w/native/native-versions.txt"
test "$(dpkg-query -W -f='${Version}' libc6)" = '2.41-12+deb13u4'
meson setup "$w/native/build" /source --prefix=/usr --libdir=lib --buildtype=release --wrap-mode=nodownload -Dplatforms=[] -Dgallium-drivers=radeonsi,softpipe -Dvulkan-drivers=[] -Dglx=disabled -Degl=enabled -Dgbm=enabled -Dglvnd=disabled -Dgles1=disabled -Dgles2=enabled -Dllvm=disabled -Damd-use-llvm=false -Ddraw-use-llvm=false -Dpower8=disabled -Dgallium-vdpau=disabled -Dgallium-va=disabled -Dgallium-xa=disabled -Dgallium-opencl=disabled -Dgallium-rusticl=false -Dlmsensors=disabled -Dzstd=disabled -Dbuild-tests=false -Dtools=drm-shim > "$w/native/configure.log" 2>&1
ninja -C "$w/native/build" -j2 > "$w/native/build.log" 2>&1
DESTDIR="$w/native/output" ninja -C "$w/native/build" install > "$w/native/install.log" 2>&1
'''
cmd=['docker','run','-d','--name','tabor-offline-shader-native-20261109-001','--cpus=2','--memory=4g','--network=bridge','-v',str(w)+':/work','-v',str(w/'mesa-source')+':/source:ro','-v',str(cache)+':/var/cache/apt/archives','--entrypoint','sh','sha256:0434a7f8dfeec379cd81d334e2a2eaa02208653e494d56334bcc486950be8a49','-c',script]
r=subprocess.run(cmd,capture_output=True,text=True);(w/'launch-offline-native.json').write_text(json.dumps({'argv':cmd,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'purpose':'native compiler-output reference only, no amd64 target archive/foundation rebuild'},indent=2)+'\n');print(r.stdout,r.stderr);r.check_returncode()
