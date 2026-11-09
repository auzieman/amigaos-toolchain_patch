from pathlib import Path
import subprocess,json
b=Path('/srv/data1/tabor-build/linux-live-001');w=b/'work/native-vertex-contract-20261109-001'
assert (w/'3d-build.exit').read_text().strip()=='0'
script='''set -e
w=/work/radeonsi-aco-20261109-001
trap 'r=$?; echo "$r" > "$w/native-vertex-spe.exit"' EXIT
meson configure "$w/build" -Dtools=drm-shim > "$w/offline-spe-configure.log" 2>&1
ninja -C "$w/build" -j2 > "$w/native-vertex-spe-build.log" 2>&1
DESTDIR="$w/offline-spe-output" ninja -C "$w/build" install > "$w/native-vertex-spe-install.log" 2>&1
'''
cmd=['docker','run','-d','--name','tabor-native-vertex-spe-20261109-003','--cpus=2','--memory=4g','--network=none','-v',str(w)+':/work/radeonsi-aco-20261109-001','-v',str(b/'work/mesa-3d-contracts-20261109-001/stage')+':/work/radeonsi-aco-20261109-001/stage:ro','-v',str(b/'tools/cxx-reference-002')+':/tools:ro','-v',str(b/'sysroot')+':/sysroot:ro','--entrypoint','sh','sha256:0434a7f8dfeec379cd81d334e2a2eaa02208653e494d56334bcc486950be8a49','-c',script]
r=subprocess.run(cmd,capture_output=True,text=True);(w/'launch-native-vertex-spe.json').write_text(json.dumps({'argv':cmd,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n');print(r.stdout,r.stderr);r.check_returncode()
