#!/usr/bin/env python3
"""Fresh source-only SPE zlib/PNG/Pixman prerequisite build; not a desktop image."""
import argparse,hashlib,json,os,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for key in ['project','cache','tools','sysroot','work']:p.add_argument('--'+key,type=Path,required=True)
p.add_argument('--image-id',required=True);p.add_argument('--jobs',type=int,default=4)
a=p.parse_args();assert 1<=a.jobs<=8 and a.image_id.startswith('sha256:')
a.work.mkdir(parents=True,exist_ok=False);stage=a.work/'stage';stage.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
lockpath=a.project/'profiles/desktop-base.lock.json';lock=json.loads(lockpath.read_text())
r={'status':'started','image_id':a.image_id,'lock_sha256':sha(lockpath),'target':'PPC32 big-endian e500v2 SPE long-double-128','jobs':a.jobs,'commands':[],'components':{},'physical_boot':False,'full_abi_validated':False}
cc=a.tools/'bin/powerpc-linux-gnuspe-gcc';cxx=a.tools/'bin/powerpc-linux-gnuspe-g++'
flags=f'--sysroot={a.sysroot} -mcpu=8548 -mabi=spe -mspe -mfloat-gprs=double -mlong-double-128 -O2 -g0 -I{stage}/usr/include'
env=os.environ.copy();env.update(PATH=str(a.tools/'bin')+':'+env['PATH'],CC=str(cc),CXX=str(cxx),AR=str(a.tools/'bin/powerpc-linux-gnuspe-ar'),RANLIB=str(a.tools/'bin/powerpc-linux-gnuspe-ranlib'),CFLAGS=flags,CXXFLAGS=flags,CPPFLAGS=f'--sysroot={a.sysroot} -I{stage}/usr/include',LDFLAGS=f'-L{stage}/usr/lib',PKG_CONFIG_SYSROOT_DIR=str(stage),PKG_CONFIG_LIBDIR=str(stage/'usr/lib/pkgconfig'))
def run(cmd,cwd):
 r['commands'].append([str(x) for x in cmd]);log.write('\n$ '+' '.join(map(str,cmd))+'\n');log.flush()
 subprocess.run(list(map(str,cmd)),cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
try:
 with (a.work/'build.log').open('w') as log:
  r['compiler_version']=subprocess.check_output([str(cc),'--version'],text=True).splitlines()[0]
  for name,comp in lock['components'].items():
   for f in comp['files']:
    file=a.cache/f['filename'];assert file.stat().st_size==f['size'] and sha(file)==f['sha256'],file
   src=a.work/(name+'-source');run(['dpkg-source','--no-check','-x',a.cache/comp['dsc'],src],a.work)
   copyrights=list(src.glob('debian/copyright'));assert copyrights
   r['components'][name]={'version':comp['version'],'copyright_sha256':sha(copyrights[0])}
   (a.work/(name+'-copyright')).write_bytes(copyrights[0].read_bytes())
   if name=='zlib':
    run(['./configure','--prefix=/usr'],src);run(['make','-j'+str(a.jobs)],src);run(['make','DESTDIR='+str(stage),'install'],src)
   elif name=='libpng':
    run(['./configure','--host=powerpc-linux-gnuspe','--build=x86_64-linux-gnu','--prefix=/usr','--disable-static','--disable-powerpc-vsx'],src)
    run(['make','-j'+str(a.jobs)],src);run(['make','DESTDIR='+str(stage),'install'],src)
   elif name=='pixman':
    # Inspect exact source options before selecting architecture-specific disables.
    options=(src/'meson_options.txt').read_text();(a.work/'pixman-meson-options.txt').write_text(options)
    cross=a.work/'spe-cross.ini'
    cross.write_text("[binaries]\nc = '"+str(cc)+"'\nar = '"+env['AR']+"'\nstrip = 'powerpc-linux-gnu-strip'\npkg-config = 'pkgconf'\n[host_machine]\nsystem = 'linux'\ncpu_family = 'ppc'\ncpu = 'e500v2'\nendian = 'big'\n[properties]\nneeds_exe_wrapper = true\nsys_root = '"+str(stage)+"'\npkg_config_libdir = ['"+str(stage/'usr/lib/pkgconfig')+"']\n[built-in options]\nc_args = "+repr(flags.split())+"\nc_link_args = ['--sysroot="+str(a.sysroot)+"', '-L"+str(stage/'usr/lib')+"']\n")
    run(['meson','setup',a.work/'pixman-build',src,'--cross-file',cross,'--prefix=/usr','--libdir=lib','--buildtype=release','-Dtests=disabled','-Ddemos=disabled','-Dgtk=disabled','-Dlibpng=enabled','-Dvmx=disabled'],a.work)
    run(['meson','compile','-C',a.work/'pixman-build','-j',a.jobs],a.work)
    run(['meson','install','-C',a.work/'pixman-build','--destdir',stage],a.work)
  r['elfs']={}
  for f in stage.rglob('*'):
   if f.is_file() and not f.is_symlink() and f.read_bytes()[:4]==b'\x7fELF':
    data=f.read_bytes();assert data[4:6]==b'\x01\x02' and data[18:20]==b'\x00\x14',f
    r['elfs'][str(f.relative_to(stage))]=sha(f)
  assert r['elfs']
  check=a.work/'desktop-base-check'
  with (a.work/'probe-build.log').open('w') as probe_log:
   subprocess.run([str(cc),*flags.split(),str(a.project/'bench/desktop-base-check.c'),'-I'+str(stage/'usr/include/pixman-1'),'-L'+str(stage/'usr/lib'),'-lpng16','-lpixman-1','-lz','-lm','-o',str(check)],env=env,stdout=probe_log,stderr=subprocess.STDOUT,check=True)
  r['probe_sha256']=sha(check)
  r['status']='source-built-prerequisites-not-runtime-tested'
except Exception as e:r.update(status='failed',error=str(e));raise
finally:(a.work/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
print(r['status'])
