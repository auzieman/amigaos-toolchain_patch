from pathlib import Path
import subprocess,json
w=Path('/srv/data1/tabor-build/linux-live-001/work/radeonsi-le-ib-20261109-001')
r=json.loads((w/'launch-patched.json').read_text());cmd=r['argv']
cmd=[x.replace('tabor-radeonsi-aco-20261109-002','tabor-radeonsi-le-ib-20261109-001').replace('/srv/data1/tabor-build/linux-live-001/work/radeonsi-aco-20261109-002:',str(w)+':').replace('patch-build.log','le-ib-build.log').replace('patch-install.log','le-ib-install.log') for x in cmd]
r=subprocess.run(cmd,capture_output=True,text=True);(w/'launch-le-ib.json').write_text(json.dumps({'argv':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n');print(r.stdout,r.stderr);r.check_returncode()
