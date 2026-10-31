#!/usr/bin/env python3
"""Build a locked X11 client chain from fresh Debian sources against SPE libc."""
import argparse,hashlib,json,os,shutil,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for n in ['project','cache','tools','sysroot','base-stage','work']:p.add_argument('--'+n,type=Path,required=True)
p.add_argument('--jobs',type=int,default=4);p.add_argument('--image-id',required=True);a=p.parse_args()
assert 1<=a.jobs<=8 and a.image_id.startswith('sha256:');a.work.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();lockpath=a.project/'profiles/x11-sources.lock.json';lock=json.loads(lockpath.read_text())
stage=a.work/'stage';shutil.copytree(a.base_stage,stage,symlinks=True)
cc=a.tools/'bin/powerpc-linux-gnuspe-gcc';flags=f'--sysroot={a.sysroot} -mcpu=8548 -mabi=spe -mspe -mfloat-gprs=double -mlong-double-128 -O2 -g0'
env=os.environ.copy();env.update(PATH=str(a.tools/'bin')+':'+env['PATH'],CC=str(cc),AR=str(a.tools/'bin/powerpc-linux-gnuspe-ar'),RANLIB=str(a.tools/'bin/powerpc-linux-gnuspe-ranlib'),CFLAGS=flags,CPPFLAGS=f'--sysroot={a.sysroot} -I{stage}/usr/include',LDFLAGS=f'-L{stage}/usr/lib -Wl,-rpath-link,{stage}/usr/lib',PKG_CONFIG_SYSROOT_DIR=str(stage),PKG_CONFIG_LIBDIR=str(stage/'usr/lib/pkgconfig')+':'+str(stage/'usr/share/pkgconfig'),PYTHONPATH=str(stage/'usr/share/xcb-proto/python'))
r={'status':'running','started_unix':time.time(),'image_id':a.image_id,'lock_sha256':sha(lockpath),'recipe_sha256':sha(Path(__file__)),'compiler_sha256':sha(cc),'flags':flags,'components':{},'commands':[],'physical_boot':False,'X11_server_tested':False}
cache_path=a.project/'profiles/x11-configure-cache.json'
cache_values=json.loads(cache_path.read_text())['values']
assert set(cache_values)=={'xorg_cv_malloc0_returns_null'} and cache_values['xorg_cv_malloc0_returns_null'] in ['yes','no']
env.update(cache_values);r['configure_cache_sha256']=sha(cache_path);r['configure_cache']=cache_values
def prune_public_libtool_metadata():
 # This stage contains public link libraries, not libltdl plugins. Absolute
 # dependency_libs entries bypass DESTDIR; use ELF and pkg-config instead.
 for archive in sorted((stage/'usr/lib').glob('*.la')):
  r.setdefault('removed_libtool_metadata',[]).append({'path':str(archive.relative_to(stage)),'sha256':sha(archive)})
  archive.unlink()
def save():
 tmp=a.work/'receipt.json.tmp';tmp.write_text(json.dumps(r,indent=2)+'\n');tmp.replace(a.work/'receipt.json')
def run(cmd,cwd):
 cmd=list(map(str,cmd));r['commands'].append(cmd);log.write('\n$ '+' '.join(cmd)+'\n');log.flush();save()
 subprocess.run(cmd,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
try:
 with (a.work/'build.log').open('w') as log:
  prune_public_libtool_metadata()
  for name,comp in lock['components'].items():
   r['active_component']=name;save();print('BUILD_START',name,comp['version'],flush=True)
   for f in comp['files']:
    file=a.cache/f['filename'];assert file.stat().st_size==f['size'] and sha(file)==f['sha256'],file
   src=a.work/(name+'-source');run(['dpkg-source','--no-check','-x',a.cache/comp['dsc'],src],a.work)
   notices=sorted((src/'debian').glob('copyright*'))+[p for p in [src/'COPYING',src/'COPYRIGHT'] if p.is_file()]
   assert notices,'No source license notices: '+name
   copyright=a.work/(name+'-copyright');copyright.write_text('\n'.join('SOURCE NOTICE: '+str(p.relative_to(src))+'\n'+p.read_text(errors='replace') for p in notices))
   opts=['--host=powerpc-linux-gnuspe','--build=x86_64-linux-gnu','--prefix=/usr','--libdir=/usr/lib','--disable-static']
   if name=='xcb-proto':opts+=['--with-python-sys-prefix','pythondir=/usr/share/xcb-proto/python']
   if name in ['xorgproto','xtrans']:opts+=['--disable-docs','--disable-specs']
   if name=='libxcb':opts+=['--disable-devel-docs','--enable-xinput','--enable-xkb']
   if name=='libx11':opts+=['--disable-specs','--without-xmlto','--without-fop','--disable-xf86bigfont']
   if not (src/'configure').is_file():run(['autoreconf','-fi'],src)
   run(['./configure',*opts],src);run(['make','-j'+str(a.jobs)],src);run(['make','DESTDIR='+str(stage),'install'],src)
   prune_public_libtool_metadata()
   r['components'][name]={'status':'built','version':comp['version'],'copyright_sha256':sha(copyright)};save();print('BUILD_PASS',name,flush=True)
  r['elfs']={}
  for f in stage.rglob('*'):
   if f.is_file() and not f.is_symlink():
    with f.open('rb') as inp:data=inp.read(20)
    if data[:4]==b'\x7fELF':
     assert data[4:6]==b'\x01\x02' and data[18:20]==b'\x00\x14',f
     r['elfs'][str(f.relative_to(stage))]=sha(f)
  r.update(status='built-not-X-server-runtime-tested',finished_unix=time.time());r.pop('active_component',None)
except Exception as e:r.update(status='failed',error=str(e),finished_unix=time.time());raise
finally:save()
print(r['status'],flush=True)
