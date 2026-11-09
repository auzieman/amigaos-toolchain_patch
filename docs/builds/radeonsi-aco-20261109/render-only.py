from pathlib import Path
import subprocess,json,difflib
w=Path('/srv/data1/tabor-build/linux-live-001/work/kmscube-build-20261109-001');p=w/'source/drm-legacy.c';s=p.read_text();needle='\tint ret;\n\n\tif (gbm->surface) {';assert s.count(needle)==1
n=s.replace(needle,'''\tint ret;

 /* Separate shader execution/readback from KMS framebuffer registration. */
 if (getenv("TABOR_RENDER_ONLY")) {
  if (!gbm->surface) return -1;
  egl->draw(0);
  return tabor_readback(gbm);
 }

\tif (gbm->surface) {''');p.write_text(n);(w/'0003-render-only-readback.patch').write_text(''.join(difflib.unified_diff(s.splitlines(True),n.splitlines(True),fromfile='a/drm-legacy.c',tofile='b/drm-legacy.c')))
r=json.loads((w/'launch-003.json').read_text());cmd=[x.replace('tabor-kmscube-build-20261109-003','tabor-kmscube-build-20261109-004').replace('build-003.log','build-004.log').replace('install-003.log','install-004.log') for x in r['argv']];r=subprocess.run(cmd,capture_output=True,text=True);print(r.stdout,r.stderr);r.check_returncode()
