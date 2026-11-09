from pathlib import Path
import subprocess,hashlib,json,shutil
w=Path('/srv/data1/tabor-build/linux-live-001/work/piglit-standard-20261109-001');runtime=Path('/home/owner/radeonsi-le-ib-live-20261109-001/root');receipt=json.loads((runtime.parent/'receipt.json').read_text());added={}
shutil.copy2(w/'piglit-build.log',w/'link-failure.log')
for n in ['libstdc++.so.6','libzstd.so.1','liblzma.so.5','libbz2.so.1.0']:
 p=runtime/'lib'/n;h=hashlib.sha256(p.read_bytes()).hexdigest();assert receipt['files']['lib/'+n]==h;shutil.copy2(p,w/'stage/usr/lib'/n);added[n]=h
(w/'completed-link-inputs.json').write_text(json.dumps({'source':'existing SHA-verified accepted runtime closure','files':added},indent=2)+'\n')
r=subprocess.run(['docker','start','tabor-piglit-standard-20261109-003'],capture_output=True,text=True);print(r.stdout,r.stderr);r.check_returncode()
