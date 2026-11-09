from pathlib import Path
import subprocess,json,difflib,hashlib
b=Path('/srv/data1/tabor-build/linux-live-001/work/radeonsi-aco-20261109-002');p=b/'mesa-source/src/gbm/backends/dri/gbm_dri.c';s=p.read_text();n=s
pairs={'X8R8G8B8':'XRGB8888','A8R8G8B8':'ARGB8888','X8B8G8R8':'XBGR8888','A8B8G8R8':'ABGR8888','B8G8R8X8':'BGRX8888','B8G8R8A8':'BGRA8888','R8G8B8X8':'RGBX8888','R8G8B8A8':'RGBA8888'}
a=s.index('static const struct gbm_dri_visual gbm_dri_visuals_table[]');z=s.index('\n};',a)
t=s[a:z]
for old,new in pairs.items():
 assert t.count('PIPE_FORMAT_'+old+'_UNORM')==1
 t=t.replace('PIPE_FORMAT_'+old+'_UNORM','PIPE_FORMAT_'+new+'_UNORM')
n=s[:a]+t+s[z:];p.write_text(n)
patch=''.join(difflib.unified_diff(s.splitlines(True),n.splitlines(True),fromfile='a/src/gbm/backends/dri/gbm_dri.c',tofile='b/src/gbm/backends/dri/gbm_dri.c'));(b/'0002-gbm-match-native-dri-8888-formats.patch').write_text(patch)
r=json.loads((b/'launch-patched.json').read_text());cmd=[x.replace('tabor-radeonsi-aco-20261109-002','tabor-radeonsi-aco-20261109-003').replace('patch-build.log','gbm-build.log').replace('patch-install.log','gbm-install.log') for x in r['argv']]
r=subprocess.run(cmd,capture_output=True,text=True);(b/'launch-gbm.json').write_text(json.dumps({'argv':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2));print(r.stdout,r.stderr);r.check_returncode()
