from pathlib import Path
import subprocess,json
w=Path('/srv/data1/tabor-build/linux-live-001/work/native-vertex-contract-20261109-001')
assert (w/'native-vertex-spe.exit').read_text().strip()=='0'
script='''set -e
trap 'r=$?; echo "$r" > /work/native-vertex-native.exit' EXIT
ninja -C /work/native/build -j2 > /work/native-vertex-native-build.log 2>&1
DESTDIR=/work/native/output ninja -C /work/native/build install > /work/native-vertex-native-install.log 2>&1
'''
cmd=['docker','run','-d','--name','tabor-offline-native-vertex-native-20261109-003','--cpus=2','--memory=4g','--network=none','-v',str(w)+':/work','-v',str(w/'mesa-source')+':/source:ro','--entrypoint','sh','sha256:92b850162c8dcc8aced3d4766e1da85d5b0a63cfcdb14c4732c0756c612d5eef','-c',script]
r=subprocess.run(cmd,capture_output=True,text=True);(w/'launch-native-vertex-native.json').write_text(json.dumps({'argv':cmd,'stdout':r.stdout,'stderr':r.stderr,'exit':r.returncode},indent=2)+'\n');r.check_returncode();print(r.stdout)
