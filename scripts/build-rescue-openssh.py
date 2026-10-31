#!/usr/bin/env python3
"""Cross-build pinned Debian OpenSSH for an explicitly reduced, key-only rescue image."""
import argparse,hashlib,json,os,shutil,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for n in ['project','cache','tools','sysroot','output']:p.add_argument('--'+n,type=Path,required=True)
p.add_argument('--image-id',required=True);a=p.parse_args()
a.output.mkdir(parents=True,exist_ok=False)
spec=json.loads((a.project/'profiles/openssh-rescue.lock.json').read_text())
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
receipt={'status':'started','image_id':a.image_id,'source_version':spec['version'],'commands':[],
         'physical_boot':False,'runtime_scope':spec['runtime_scope']}
with (a.output/'build.log').open('w') as log:
 def run(command,cwd=None,env=None):
  command=[str(x) for x in command];receipt['commands'].append(command)
  log.write('$ '+repr(command)+'\n');log.flush()
  subprocess.run(command,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 try:
  for item in spec['files']:
   path=a.cache/item['filename'];assert path.stat().st_size==item['size'] and sha(path)==item['sha256']
  source=a.output/'source';run(['dpkg-source','--no-check','-x',a.cache/spec['dsc'],source])
  flags=json.loads((a.project/'profiles/images/a1222-minimal.json').read_text())['build_policy']['target_runtime_cflags']
  cross=str(a.tools/'bin/powerpc-linux-gnuspe-')
  compiler=cross+'gcc --sysroot='+str(a.sysroot)+' -isystem '+str(a.sysroot/'usr/include')+' -B'+str(a.sysroot/'usr/lib')+'/ '+' '.join(flags)
  env={**os.environ,'CC':compiler,'AR':cross+'ar','RANLIB':cross+'ranlib',
       'CFLAGS':'-O2','LDFLAGS':'--sysroot='+str(a.sysroot)+' -static',
       'PKG_CONFIG_LIBDIR':str(a.sysroot/'usr/lib/pkgconfig'),'PKG_CONFIG_SYSROOT_DIR':str(a.sysroot)}
  receipt['compiler']=compiler
  options=['--build=x86_64-linux-gnu','--host=powerpc-linux-gnuspe','--prefix=/usr',
   '--sysconfdir=/etc/ssh','--libexecdir=/usr/lib/openssh','--with-privsep-user=sshd',
   '--with-privsep-path=/var/empty','--with-sandbox=seccomp_filter','--without-openssl',
   '--without-zlib','--without-pam','--without-selinux','--without-libedit','--without-ldns',
   '--disable-security-key']
  # Debian patches configure.ac; regenerate instead of touching timestamps or
  # bypassing upstream's stale-configure guard.
  run(['autoreconf','-fi'],source,env)
  run([source/'configure',*options],source,env)
  run(['make','-j2'],source,env)
  payload=a.output/'payload';files=[]
  for name,target in {'ssh':'usr/bin/ssh','ssh-keygen':'usr/bin/ssh-keygen',
   'scp':'usr/bin/scp','sftp':'usr/bin/sftp','sshd':'usr/sbin/sshd',
   'sshd-session':'usr/lib/openssh/sshd-session','sshd-auth':'usr/lib/openssh/sshd-auth',
   'sftp-server':'usr/lib/openssh/sftp-server'}.items():
   dest=payload/target;dest.parent.mkdir(parents=True,exist_ok=True)
   run(['powerpc-linux-gnu-strip','-o',dest,source/name])
   header=subprocess.check_output(['powerpc-linux-gnu-readelf','-l',str(dest)],text=True)
   assert 'INTERP' not in header,name
   files.append({'path':target,'sha256':sha(dest),'mode':0o755})
  licenses=payload/'usr/share/licenses/openssh';licenses.mkdir(parents=True)
  for filename,src in [('LICENCE',source/'LICENCE'),('debian-copyright',source/'debian/copyright')]:
   shutil.copyfile(src,licenses/filename)
   path=licenses/filename;files.append({'path':str(path.relative_to(payload)),'sha256':sha(path),'mode':0o644})
  receipt.update(status='static-openssh-cross-built-not-executed',files=files,
                 crypto='Ed25519/Curve25519/ChaCha20 built in; no OpenSSL/RSA',sandbox='seccomp_filter; kernel filter support required')
  (a.output/'payload-manifest.json').write_text(json.dumps({'files':files},indent=2)+'\n')
 except Exception as error:
  receipt.update(status='failed',error=str(error));raise
 finally:(a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'])
