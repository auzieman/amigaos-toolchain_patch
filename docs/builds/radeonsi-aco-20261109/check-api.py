from pathlib import Path
import subprocess,json
w=Path('/srv/data1/tabor-build/linux-live-001/work/kmscube-build-20261109-001');p=w/'source/drm-legacy.c';s=p.read_text();needle='  glClear(GL_COLOR_BUFFER_BIT);';assert s.count(needle)==1
extra=r'''  GLfloat clear[4]={0}; unsigned bits[4];
  glGetFloatv(GL_COLOR_CLEAR_VALUE,clear); memcpy(bits,clear,sizeof(bits));
  fprintf(stderr,"TABOR_CLEAR_API bits=%08x,%08x,%08x,%08x error=%x\n",bits[0],bits[1],bits[2],bits[3],glGetError());
'''
p.write_text(s.replace(needle,extra+needle))
r=json.loads((w/'launch-003.json').read_text());cmd=[x.replace('tabor-kmscube-build-20261109-003','tabor-kmscube-build-20261109-006').replace('build-003.log','build-006.log').replace('install-003.log','install-006.log') for x in r['argv']];r=subprocess.run(cmd,capture_output=True,text=True);print(r.stdout,r.stderr);r.check_returncode()
