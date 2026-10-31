#!/usr/bin/env python3
"""Build OpenSSH's crypt dependency into a new sysroot overlay, preserving the reference."""
import argparse,hashlib,json,os,shutil,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for n in ['project','cache','tools','sysroot','output']:p.add_argument('--'+n,type=Path,required=True)
p.add_argument('--image-id',required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
spec=json.loads((a.project/'profiles/libxcrypt.lock.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'status':'started','image_id':a.image_id,'version':spec['version'],'commands':[]}
with (a.output/'build.log').open('w') as log:
 def run(c,cwd=None,env=None):
  c=[str(x) for x in c];r['commands'].append(c);log.write('$ '+repr(c)+'\n');log.flush()
  subprocess.run(c,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 try:
  for f in spec['files']:assert (a.cache/f['filename']).stat().st_size==f['size'] and sha(a.cache/f['filename'])==f['sha256']
  source=a.output/'source';run(['dpkg-source','--no-check','-x',a.cache/spec['dsc'],source])
  overlay=a.output/'sysroot';shutil.copytree(a.sysroot,overlay,symlinks=True)
  flags=json.loads((a.project/'profiles/images/a1222-minimal.json').read_text())['build_policy']['target_runtime_cflags']
  cross=str(a.tools/'bin/powerpc-linux-gnuspe-')
  compiler=cross+'gcc --sysroot='+str(overlay)+' -isystem '+str(overlay/'usr/include')+' -B'+str(overlay/'usr/lib')+'/ '+' '.join(flags)
  env={**os.environ,'CC':compiler,'AR':cross+'ar','RANLIB':cross+'ranlib','CFLAGS':'-O2'};r['compiler']=compiler
  run(['autoreconf','-fi'],source,env)
  run([source/'configure','--build=x86_64-linux-gnu','--host=powerpc-linux-gnuspe','--prefix=/usr','--libdir=/usr/lib','--disable-shared','--enable-static'],source,env)
  run(['make','-j2'],source,env);run(['make','DESTDIR='+str(overlay),'install'],source,env)
  r.update(status='libxcrypt-installed-in-fresh-overlay',libcrypt_sha256=sha(overlay/'usr/lib/libcrypt.a'),header_sha256=sha(overlay/'usr/include/crypt.h'))
 except Exception as e:r.update(status='failed',error=str(e));raise
 finally:(a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
print(r['status'])
