from pathlib import Path
import json,subprocess,difflib
w=Path('/srv/data1/tabor-build/linux-live-001/work/kmscube-build-20261109-001')
p=w/'source/drm-legacy.c';s=p.read_text();needle='  egl->draw(0);\n  return tabor_readback(gbm);';assert s.count(needle)==1
n=s.replace(needle,'''  GLint vp[4]={0}, binding=-1;
  unsigned char pixel[4]={0};
  glGetIntegerv(GL_VIEWPORT,vp);
  glGetIntegerv(GL_FRAMEBUFFER_BINDING,&binding);
  fprintf(stderr,"TABOR_DRAW_STATE viewport=%d,%d,%d,%d framebuffer=%d status=%x error=%x\\n",vp[0],vp[1],vp[2],vp[3],binding,glCheckFramebufferStatus(GL_FRAMEBUFFER),glGetError());
  glDisable(GL_SCISSOR_TEST);
  glColorMask(GL_TRUE,GL_TRUE,GL_TRUE,GL_TRUE);
  glClearColor(1.0f,0.0f,0.0f,1.0f);
  glClear(GL_COLOR_BUFFER_BIT);
  glFinish();
  glReadPixels(0,0,1,1,GL_RGBA,GL_UNSIGNED_BYTE,pixel);
  fprintf(stderr,"TABOR_RED_CLEAR rgba=%u,%u,%u,%u error=%x\\n",pixel[0],pixel[1],pixel[2],pixel[3],glGetError());
  if(getenv("TABOR_CLEAR_ONLY")) return pixel[0]>240 && pixel[1]<16 && pixel[2]<16 ? 0 : -1;
  egl->draw(0);
  return tabor_readback(gbm);''')
p.write_text(n);patch=list(difflib.unified_diff(s.splitlines(True),n.splitlines(True),fromfile='a/drm-legacy.c',tofile='b/drm-legacy.c'))
p=w/'source/drm-common.c';s=p.read_text();needle='\tif (ret) {\n\t\tprintf("failed to create fb: %s\\n", strerror(errno));';assert s.count(needle)==1
n=s.replace(needle,'''\tfprintf(stderr,"TABOR_ADDFB fd=%d size=%ux%u format=%08x handle=%u stride=%u offset=%u flags=%x ret=%d errno=%d\\n",drm_fd,width,height,format,handles[0],strides[0],offsets[0],flags,ret,errno);
'''+needle);p.write_text(n);patch+=list(difflib.unified_diff(s.splitlines(True),n.splitlines(True),fromfile='a/drm-common.c',tofile='b/drm-common.c'));(w/'0004-clear-and-framebuffer-boundaries.patch').write_text(''.join(patch))
r=json.loads((w/'launch-003.json').read_text());cmd=[x.replace('tabor-kmscube-build-20261109-003','tabor-kmscube-build-20261109-005').replace('build-003.log','build-005.log').replace('install-003.log','install-005.log') for x in r['argv']];r=subprocess.run(cmd,capture_output=True,text=True);print(r.stdout,r.stderr);r.check_returncode()
