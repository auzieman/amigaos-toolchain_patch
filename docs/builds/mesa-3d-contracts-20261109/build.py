from pathlib import Path
import subprocess,json
b=Path('/srv/data1/tabor-build/linux-live-001');w=b/'work/mesa-3d-contracts-20261109-001'
assert json.loads((w/'query-contract-check.json').read_text())['status']=='PASS'
cmd=['docker','run','-d','--name','tabor-mesa-3d-contracts-20261109-001','--cpus=2','--memory=4g','--network=none','-v',str(w)+':/work/radeonsi-aco-20261109-001','-v',str(b/'tools/cxx-reference-002')+':/tools:ro','-v',str(b/'sysroot')+':/sysroot:ro','--entrypoint','sh','sha256:0434a7f8dfeec379cd81d334e2a2eaa02208653e494d56334bcc486950be8a49','-c',
'''set -e
w=/work/radeonsi-aco-20261109-001
trap 'r=$?; echo "$r" > "$w/3d-build.exit"' EXIT
ninja -C "$w/build" -j2 > "$w/3d-build.log" 2>&1
DESTDIR="$w/output" ninja -C "$w/build" install > "$w/3d-install.log" 2>&1
''']
r=subprocess.run(cmd,capture_output=True,text=True);(w/'launch-3d.json').write_text(json.dumps({'argv':cmd,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n');print(r.stdout,r.stderr);r.check_returncode()
