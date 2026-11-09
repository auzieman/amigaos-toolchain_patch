from pathlib import Path
import subprocess,json,difflib
w=Path('/srv/data1/tabor-build/linux-live-001/work/kmscube-build-20261109-001');p=w/'source/drm-common.c';s=p.read_text();needle='\tfprintf(stderr,"TABOR_ADDFB fd=';i=s.index(needle)
extra='''
 /* drm_mode_addfb2_ioctl deliberately rejects unconverted BE drivers.
  * Only legacy-compatible, single-plane, zero-offset RGB may fall back. */
 if (ret == -EOPNOTSUPP && offsets[0] == 0 &&
     (format == GBM_FORMAT_XRGB8888 || format == GBM_FORMAT_ARGB8888)) {
  uint8_t depth = format == GBM_FORMAT_ARGB8888 ? 32 : 24;
  ret = drmModeAddFB(drm_fd, width, height, depth, 32,
                    strides[0], handles[0], &fb->fb_id);
  fprintf(stderr,"TABOR_LEGACY_ADDFB ret=%d id=%u\\n",ret,fb->fb_id);
 }
'''
n=s[:i]+extra+s[i:];p.write_text(n);(w/'0005-kms-legacy-big-endian-fallback.patch').write_text(''.join(difflib.unified_diff(s.splitlines(True),n.splitlines(True),fromfile='a/drm-common.c',tofile='b/drm-common.c')))
r=json.loads((w/'launch-003.json').read_text());cmd=[x.replace('tabor-kmscube-build-20261109-003','tabor-kmscube-build-20261109-007').replace('build-003.log','build-007.log').replace('install-003.log','install-007.log') for x in r['argv']];r=subprocess.run(cmd,capture_output=True,text=True);print(r.stdout,r.stderr);r.check_returncode()
