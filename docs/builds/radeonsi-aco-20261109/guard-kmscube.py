from pathlib import Path
import json,subprocess,difflib
w=Path('/srv/data1/tabor-build/linux-live-001/work/kmscube-build-20261109-001')
p=w/'source/common.c';s=p.read_text()
needle='gl_exts = (char *) glGetString(GL_EXTENSIONS);'
guard="""
 if (getenv("TABOR_REQUIRE_HARDWARE")) {
  const char *renderer = (const char *)glGetString(GL_RENDERER);
  if (!renderer || strstr(renderer, "softpipe") || strstr(renderer, "llvmpipe") ||
      !(strstr(renderer, "Radeon") || strstr(renderer, "RADEON") || strstr(renderer, "AMD"))) {
   fprintf(stderr, "TABOR_HARDWARE_RENDERER_REJECTED=%s\\n", renderer ? renderer : "none");
   return -1;
  }
 }
"""
assert s.count(needle)==1
if 'TABOR_REQUIRE_HARDWARE' not in s:
 n=s.replace(needle,needle+guard);p.write_text(n)
 (w/'0002-reject-software-fallback.patch').write_text(''.join(difflib.unified_diff(s.splitlines(True),n.splitlines(True),fromfile='a/common.c',tofile='b/common.c')))
r=json.loads((w/'launch-002.json').read_text());cmd=r['argv'];cmd=[x.replace('tabor-kmscube-build-20261109-002','tabor-kmscube-build-20261109-003').replace('build-002.log','build-003.log').replace('install-002.log','install-003.log') for x in cmd]
r=subprocess.run(cmd,capture_output=True,text=True);(w/'launch-003.json').write_text(json.dumps({'argv':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2));print(r.stdout,r.stderr);r.check_returncode()
