from pathlib import Path
import json,hashlib,subprocess,difflib
b=Path('/srv/data1/tabor-build/linux-live-001');w=b/'work/kmscube-build-20261109-001';stage=w/'stage';records=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for dirname,names,extra in [('gcc-runtime-package-003',['libgcc-s1','libstdc++6'],False),('port-pipeline-20261104-010-base-libraries-elfutils',['libzstd1','zlib1g','liblzma5','libbz2-1.0'],True)]:
 p=b/'work'/dirname;r=json.loads((p/'receipt.json').read_text())
 for name in names:
  if extra:
   f=next((p/'extra-packages').glob(name+'_*.deb'));m=next(x for x in r['extra_package_inputs'] if x['file']==f.name)
  else:
   n=next(n for n in r['packages'] if n.split('_')[0]==name);f=p/n;m=r['packages'][n]
  assert sha(f)==m['sha256'];subprocess.run(['dpkg-deb','-x',str(f),str(stage)],check=True);records.append({'file':str(f),'sha256':sha(f)})
(w/'runtime-dependencies.json').write_text(json.dumps(records,indent=2)+'\n')
patch=[]
p=w/'source/kmscube.c';s=p.read_text();i=s.index('{',s.index('int main('))+1;n=s[:i]+'\n\tsetvbuf(stdout, NULL, _IOLBF, 0);\n'+s[i:];patch+=list(difflib.unified_diff(s.splitlines(True),n.splitlines(True),fromfile='a/kmscube.c',tofile='b/kmscube.c'));p.write_text(n)
p=w/'source/drm-legacy.c';s=p.read_text();helper=r'''
/* Test-only first-frame evidence; disabled unless TABOR_READBACK is set. */
static int tabor_readback(const struct gbm *gbm)
{
 unsigned w=gbm->width,h=gbm->height,colored=0;
 unsigned char *pixels=malloc((size_t)w*h*4);
 if(!pixels)return -1;
 glFinish();
 glReadPixels(0,0,w,h,GL_RGBA,GL_UNSIGNED_BYTE,pixels);
 unsigned error=glGetError();
 if(error){fprintf(stderr,"TABOR_GL_ERROR=%x\n",error);free(pixels);return -1;}
 FILE *f=fopen("/run/kmscube.ppm","wb");
 if(!f){free(pixels);return -1;}
 fprintf(f,"P6\n%u %u\n255\n",w,h);
 for(unsigned y=h;y-- >0;)for(unsigned x=0;x<w;x++){
  unsigned char *p=pixels+((size_t)y*w+x)*4;
  unsigned hi=p[0]>p[1]?p[0]:p[1],lo=p[0]<p[1]?p[0]:p[1];
  if(p[2]>hi)hi=p[2];if(p[2]<lo)lo=p[2];if(hi-lo>32)colored++;
  if(fwrite(p,1,3,f)!=3){fclose(f);free(pixels);return -1;}
 }
 int failed=fclose(f);free(pixels);
 fprintf(stderr,"TABOR_GL_READBACK=%s colored=%u width=%u height=%u\n",!failed&&colored>1000?"PASS":"FAIL",colored,w,h);
 return failed||colored<=1000?-1:0;
}
'''
n=s.replace('#include <errno.h>','#include <errno.h>\n#include <stdlib.h>');n=n.replace('static struct drm drm;','static struct drm drm;\n'+helper);needle='\t\tegl->draw(i++);';assert n.count(needle)==1;n=n.replace(needle,needle+'\n\t\tif(i==1 && getenv("TABOR_READBACK") && tabor_readback(gbm))return -1;')
patch+=list(difflib.unified_diff(s.splitlines(True),n.splitlines(True),fromfile='a/drm-legacy.c',tofile='b/drm-legacy.c'));p.write_text(n);(w/'0001-bounded-first-frame-evidence.patch').write_text(''.join(patch))
cmd=['docker','run','-d','--name','tabor-kmscube-build-20261109-002','--cpus=1','--memory=1g','--network=none','-v',str(w)+':/work/kmscube-build-20261109-001','-v',str(b/'tools/cxx-reference-002')+':/tools:ro','-v',str(b/'sysroot')+':/sysroot:ro','--entrypoint','sh','sha256:0434a7f8dfeec379cd81d334e2a2eaa02208653e494d56334bcc486950be8a49','-c',
'''w=/work/kmscube-build-20261109-001
ninja -C "$w/build" -j1 > "$w/build-002.log" 2>&1 || { echo compile-failed > "$w/status"; exit 1; }
DESTDIR="$w/output" ninja -C "$w/build" install > "$w/install-002.log" 2>&1 || { echo install-failed > "$w/status"; exit 1; }
echo built-with-readback-not-runtime-validated > "$w/status"''']
r=subprocess.run(cmd,capture_output=True,text=True);(w/'launch-002.json').write_text(json.dumps({'argv':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n');r.check_returncode();print(r.stdout)
p=b/'work/radeonsi-aco-20261109-002/patch-receipt.json';r=json.loads(p.read_text());r['historical_container_path_alias']='/work/radeonsi-aco-20261109-001';p.write_text(json.dumps(r,indent=2)+'\n')
