from pathlib import Path
import hashlib,json,shutil,subprocess
base=Path('/srv/data1/tabor-build/linux-live-001');parent=base/'work/software-gl-002';w=base/'work/radeonsi-aco-20261109-001';w.mkdir(exist_ok=False);stage=w/'stage';(stage/'usr/lib').mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Retain the already reviewed pinned Mesa source; SDK stays mounted read-only.
subprocess.run(['cp','-a','--reflink=auto',str(parent/'mesa-source'),str(w/'mesa-source')],check=True)
old=base/'work/hardware-x-002/stage';shutil.copytree(old/'usr/include',stage/'usr/include',symlinks=True)
for p in (old/'usr/lib').iterdir():
 if p.is_file() or p.is_symlink():shutil.copy2(p,stage/'usr/lib'/p.name,follow_symlinks=False)
shutil.copytree(old/'usr/lib/pkgconfig',stage/'usr/lib/pkgconfig',symlinks=True)
inputs=[]
for dirname,names in [
 ('port-pipeline-20261104-017-base-libraries-libdrm',['libdrm-dev','libdrm2','libdrm-amdgpu1']),
 ('port-pipeline-20261104-010-base-libraries-elfutils',['libelf-dev','libelf1t64'])]:
 p=base/'work'/dirname;r=json.loads((p/'receipt.json').read_text());assert r['status']=='debian-packages-built-not-target-installed'
 for name in names:
  matches=[(n,m) for n,m in r['packages'].items() if n.split('_')[0]==name];assert len(matches)==1,(name,matches)
  n,m=matches[0];f=p/n;assert sha(f)==m['sha256'];subprocess.run(['dpkg-deb','-x',str(f),str(stage)],check=True)
  inputs.append({'file':str(f),'sha256':sha(f),'receipt_sha256':sha(p/'receipt.json')})
text=(parent/'spe-cross.ini').read_text().replace('/work/software-gl-002','/work/radeonsi-aco-20261109-001')
text=text.replace("pkg_config_libdir = [", "pkg_config_libdir = ['/work/radeonsi-aco-20261109-001/stage/usr/lib/powerpc-linux-gnuspe/pkgconfig', ")
text=text.replace("'-L/work/radeonsi-aco-20261109-001/stage/usr/lib'", "'-L/work/radeonsi-aco-20261109-001/stage/usr/lib/powerpc-linux-gnuspe', '-Wl,-rpath-link,/work/radeonsi-aco-20261109-001/stage/usr/lib/powerpc-linux-gnuspe', '-L/work/radeonsi-aco-20261109-001/stage/usr/lib'")
(w/'spe-cross.ini').write_text(text)
cc=base/'tools/cxx-reference-002/bin/powerpc-linux-gnuspe-gcc';assert sha(cc)=='cd426582533f655db4af7f3b4a694a9f122dbc77eb0080204649c4144fba09ba'
(w/'inputs.json').write_text(json.dumps({'purpose':'isolated hardware-renderer qualification; not a Debian package build or SDK14 promotion','parent_receipt_sha256':sha(parent/'receipt.json'),'compiler_sha256':sha(cc),'debian_dependencies':inputs,'source_build_options':'radeonsi+ACO, EGL+GBM, no LLVM; same pinned Mesa25.0.7 source as software control','abi':'powerpcspe PPC32 BE e500v2 SPE GPR double long-double128'},indent=2)+'\n')
cmd=['docker','run','-d','--name','tabor-radeonsi-aco-20261109-001','--cpus=2','--memory=4g','--network=none','-v',str(base/'work')+':/work','-v',str(base/'tools/cxx-reference-002')+':/tools:ro','-v',str(base/'sysroot')+':/sysroot:ro','--entrypoint','sh','sha256:0434a7f8dfeec379cd81d334e2a2eaa02208653e494d56334bcc486950be8a49','-c',
'''set -e
w=/work/radeonsi-aco-20261109-001
meson setup "$w/build" "$w/mesa-source" --cross-file "$w/spe-cross.ini" --prefix=/usr --libdir=lib --buildtype=release --wrap-mode=nodownload -Dplatforms=[] -Dgallium-drivers=radeonsi,softpipe -Dvulkan-drivers=[] -Dglx=disabled -Degl=enabled -Dgbm=enabled -Dglvnd=disabled -Dgles1=disabled -Dgles2=enabled -Dllvm=disabled -Damd-use-llvm=false -Ddraw-use-llvm=false -Dpower8=disabled -Dgallium-vdpau=disabled -Dgallium-va=disabled -Dgallium-xa=disabled -Dgallium-opencl=disabled -Dgallium-rusticl=false -Dlmsensors=disabled -Dzstd=disabled -Dbuild-tests=false > "$w/configure.log" 2>&1 || { echo configure-failed > "$w/status"; exit 1; }
echo compiling > "$w/status"
ninja -C "$w/build" -j2 > "$w/build.log" 2>&1 || { echo compile-failed > "$w/status"; exit 1; }
DESTDIR="$w/output" ninja -C "$w/build" install > "$w/install.log" 2>&1 || { echo install-failed > "$w/status"; exit 1; }
echo built-not-runtime-validated > "$w/status"
''']
r=subprocess.run(cmd,capture_output=True,text=True);(w/'launch.json').write_text(json.dumps({'argv':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n');r.check_returncode();print(r.stdout)
