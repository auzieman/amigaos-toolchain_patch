from pathlib import Path
import subprocess,json,shutil
b=Path('/srv/data1/tabor-build/linux-live-001');parent=b/'work/radeonsi-aco-20261109-001';w=b/'work/kmscube-build-20261109-001';w.mkdir(exist_ok=False)
subprocess.run(['cp','-a','--reflink=auto',str(parent/'stage'),str(w/'stage')],check=True)
subprocess.run(['cp','-a',str(parent/'output')+'/.',str(w/'stage')],check=True)
subprocess.run(['cp','-a',str(b/'work/kmscube-intake-20261109-001/source'),str(w/'source')],check=True)
s=(parent/'spe-cross.ini').read_text().replace('/work/radeonsi-aco-20261109-001','/work/kmscube-build-20261109-001');(w/'spe-cross.ini').write_text(s)
cmd=['docker','run','-d','--name','tabor-kmscube-build-20261109-001','--cpus=1','--memory=1g','--network=none','-v',str(w)+':/work/kmscube-build-20261109-001','-v',str(b/'tools/cxx-reference-002')+':/tools:ro','-v',str(b/'sysroot')+':/sysroot:ro','--entrypoint','sh','sha256:0434a7f8dfeec379cd81d334e2a2eaa02208653e494d56334bcc486950be8a49','-c',
'''w=/work/kmscube-build-20261109-001
meson setup "$w/build" "$w/source" --cross-file "$w/spe-cross.ini" --prefix=/usr --libdir=lib --wrap-mode=nodownload -Dgstreamer=disabled > "$w/configure.log" 2>&1 || { echo configure-failed > "$w/status"; exit 1; }
ninja -C "$w/build" -j1 > "$w/build.log" 2>&1 || { echo compile-failed > "$w/status"; exit 1; }
DESTDIR="$w/output" ninja -C "$w/build" install > "$w/install.log" 2>&1 || { echo install-failed > "$w/status"; exit 1; }
echo built-not-runtime-validated > "$w/status"''']
r=subprocess.run(cmd,capture_output=True,text=True);(w/'launch.json').write_text(json.dumps({'argv':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n');r.check_returncode();print(r.stdout)
