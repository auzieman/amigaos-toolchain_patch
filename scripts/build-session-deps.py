#!/usr/bin/env python3
"""Fresh SPE software-session dependencies and virtual X server; no GPU claim."""
import argparse,hashlib,json,os,shutil,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for n in ['project','cache','tools','sysroot','base-stage','work']:p.add_argument('--'+n,type=Path,required=True)
p.add_argument('--source-lock',default='profiles/session-sources.lock.json');p.add_argument('--extra-stage',type=Path);p.add_argument('--image-id',required=True);p.add_argument('--jobs',type=int,default=4);p.add_argument('--components',default='')
a=p.parse_args();assert 1<=a.jobs<=8;a.work.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();stage=a.work/'stage';shutil.copytree(a.base_stage,stage,symlinks=True)
if a.extra_stage:
 for f in a.extra_stage.rglob('*'):
  if f.is_dir():continue
  dest=stage/f.relative_to(a.extra_stage);assert not dest.exists() and not dest.is_symlink(),dest
  dest.parent.mkdir(parents=True,exist_ok=True)
  if f.is_symlink():dest.symlink_to(os.readlink(f))
  else:shutil.copy2(f,dest)
if (stage/'work').exists():shutil.rmtree(stage/'work')
lockpath=a.project/a.source_lock;lock=json.loads(lockpath.read_text())
cc=a.tools/'bin/powerpc-linux-gnuspe-gcc';cxx=a.tools/'bin/powerpc-linux-gnuspe-g++'
abi=['--sysroot='+str(a.sysroot),'-mcpu=8548','-mabi=spe','-mspe','-mfloat-gprs=double','-mlong-double-128','-O2','-g0']
cflags=abi+['-I'+str(stage/'usr/include')];ldflags=['-L'+str(stage/'usr/lib'),'-Wl,-rpath-link,'+str(stage/'usr/lib')]
env=os.environ.copy();env.update(PATH=str(a.tools/'bin')+':'+env['PATH'],CC=str(cc),CXX=str(cxx),AR=str(a.tools/'bin/powerpc-linux-gnuspe-ar'),RANLIB=str(a.tools/'bin/powerpc-linux-gnuspe-ranlib'),CFLAGS=' '.join(cflags),CXXFLAGS=' '.join(cflags),CPPFLAGS=' '.join([abi[0],cflags[-1]]),LDFLAGS=' '.join(ldflags),PKG_CONFIG_SYSROOT_DIR=str(stage),PKG_CONFIG_LIBDIR=str(stage/'usr/lib/pkgconfig')+':'+str(stage/'usr/share/pkgconfig'),xorg_cv_malloc0_returns_null='yes')
r={'status':'running','image_id':a.image_id,'lock_sha256':sha(lockpath),'recipe_sha256':sha(Path(__file__)),'compiler_sha256':sha(cc),'flags':cflags,'components':{},'commands':[],'physical_boot':False,'GPU_validated':False}
r['input_stage_files']={str(p.relative_to(a.base_stage)):sha(p) for p in a.base_stage.rglob('*') if p.is_file() and not p.is_symlink()}
def save():
 t=a.work/'receipt.tmp';t.write_text(json.dumps(r,indent=2)+'\n');t.replace(a.work/'receipt.json')
def run(cmd,cwd):
 cmd=list(map(str,cmd));r['commands'].append(cmd);log.write('\n$ '+' '.join(cmd)+'\n');log.flush();save();subprocess.run(cmd,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
def autotools(src,opts):
 if not (src/'configure').exists() or src.name.startswith('fontconfig'):run(['autoreconf','-fi'],src)
 run(['./configure','--host=powerpc-linux-gnuspe','--build=x86_64-linux-gnu','--prefix=/usr','--libdir=/usr/lib','--disable-static',*opts],src)
 run(['make','-j'+str(a.jobs)],src);run(['make','DESTDIR='+str(stage),'install'],src)
cross=a.work/'spe-cross.ini'
cross.write_text("[binaries]\nc = '"+str(cc)+"'\ncpp = '"+str(cxx)+"'\nar = '"+env['AR']+"'\nstrip = 'powerpc-linux-gnu-strip'\npkg-config = 'pkgconf'\n[host_machine]\nsystem = 'linux'\ncpu_family = 'ppc'\ncpu = 'e500v2'\nendian = 'big'\n[properties]\nneeds_exe_wrapper = true\nsys_root = '"+str(stage)+"'\npkg_config_libdir = ['"+str(stage/'usr/lib/pkgconfig')+"', '"+str(stage/'usr/share/pkgconfig')+"']\n[built-in options]\nc_args = "+repr(cflags)+"\ncpp_args = "+repr(cflags)+"\nc_link_args = "+repr([abi[0],*ldflags])+"\ncpp_link_args = "+repr([abi[0],*ldflags])+"\n")
cmake=a.work/'spe-cmake.cmake';cmake.write_text(f'''set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR ppc)
set(CMAKE_C_COMPILER {cc})
set(CMAKE_CXX_COMPILER {cxx})
set(CMAKE_SYSROOT {a.sysroot})
set(CMAKE_FIND_ROOT_PATH {stage} {a.sysroot})
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)
set(CMAKE_C_FLAGS "{' '.join(cflags)}")
set(CMAKE_CXX_FLAGS "{' '.join(cflags)}")
set(CMAKE_EXE_LINKER_FLAGS "{' '.join(ldflags)}")
set(CMAKE_SHARED_LINKER_FLAGS "{' '.join(ldflags)}")
''')
def meson(src,name,opts):
 build=a.work/(name+'-build');run(['meson','setup',build,src,'--cross-file',cross,'--prefix=/usr','--libdir=lib','--sysconfdir=/etc','--localstatedir=/var','--buildtype=release','--wrap-mode=nodownload',*opts],a.work);run(['meson','compile','-C',build,'-j',a.jobs],a.work);run(['meson','install','-C',build,'--destdir',stage],a.work)
def cmakebuild(src,name,opts):
 build=a.work/(name+'-build');run(['cmake','-S',src,'-B',build,'-G','Ninja','-DCMAKE_TOOLCHAIN_FILE='+str(cmake),'-DCMAKE_INSTALL_PREFIX=/usr','-DCMAKE_INSTALL_LIBDIR=/usr/lib','-DCMAKE_BUILD_TYPE=Release',*opts],a.work);run(['cmake','--build',build,'--parallel',a.jobs],a.work)
 old=env.get('DESTDIR');env['DESTDIR']=str(stage)
 try:run(['cmake','--install',build],a.work)
 finally:
  if old is None:env.pop('DESTDIR',None)
  else:env['DESTDIR']=old
try:
 with (a.work/'build.log').open('w') as log:
  selected=a.components.split(',') if a.components else [n for n in lock['components'] if n!='fonts-dejavu']
  for name in selected:
   comp=lock['components'][name];r['active_component']=name;save();print('BUILD_START',name,flush=True)
   for f in comp['files']:
    p=a.cache/f['filename'];assert p.stat().st_size==f['size'] and sha(p)==f['sha256'],p
   src=a.work/(name+'-source');run(['dpkg-source','--no-check','-x',a.cache/comp['dsc'],src],a.work)
   notices=sorted((src/'debian').glob('copyright*'))+[p for p in [src/'COPYING',src/'COPYRIGHT',src/'LICENSE'] if p.is_file()];assert notices
   notice=a.work/(name+'-copyright');notice.write_text('\n'.join(str(p.relative_to(src))+'\n'+p.read_text(errors='replace') for p in notices))
   if name=='expat':cmakebuild(src/'expat',name,['-DEXPAT_BUILD_TOOLS=OFF','-DEXPAT_BUILD_TESTS=OFF','-DEXPAT_BUILD_EXAMPLES=OFF','-DEXPAT_BUILD_DOCS=OFF','-DEXPAT_SHARED_LIBS=ON'])
   elif name=='freetype':autotools(src,['--without-bzip2','--without-harfbuzz','--without-brotli','--with-zlib=yes','--with-png=yes'])
   elif name=='fontconfig':meson(src,name,['-Ddoc=disabled','-Dtests=disabled','-Dnls=disabled','-Dcache-build=disabled','-Dtools=enabled'])
   elif name=='libjpeg-turbo':cmakebuild(src,name,['-DENABLE_SHARED=ON','-DENABLE_STATIC=OFF','-DWITH_SIMD=OFF','-DWITH_TURBOJPEG=OFF'])
   elif name=='fribidi':meson(src,name,['-Ddocs=false','-Dtests=false','-Dbin=false'])
   elif name=='harfbuzz':meson(src,name,['-Dglib=disabled','-Dgobject=disabled','-Dcairo=disabled','-Dchafa=disabled','-Dicu=disabled','-Dtests=disabled','-Ddocs=disabled','-Dintrospection=disabled','-Dutilities=disabled','-Dfreetype=enabled','-Dbenchmark=disabled'])
   elif name=='openssl':
    run(['perl','Configure','linux-ppc','--prefix=/usr','--libdir=lib','shared','no-asm','no-tests','no-module','no-engine','no-legacy'],src);run(['make','-j'+str(a.jobs)],src);run(['make','DESTDIR='+str(stage),'install_sw'],src)
   elif name=='curl':autotools(src,['--with-openssl='+str(stage/'usr'),'--without-libpsl','--without-libidn2','--without-brotli','--without-zstd','--without-nghttp2','--without-nghttp3','--without-ngtcp2','--disable-ldap','--disable-ldaps','--disable-manual','--without-libssh2','--without-librtmp'])
   elif name=='dbus':meson(src,name,['-Dapparmor=disabled','-Dselinux=disabled','-Dlibaudit=disabled','-Dsystemd=disabled','-Ddoxygen_docs=disabled','-Dducktype_docs=disabled','-Dxml_docs=disabled','-Dmodular_tests=disabled','-Dinstalled_tests=false','-Dx11_autolaunch=disabled'])
   elif name=='lua5.1':
    (src/'src/lua5.1-deb-multiarch.h').write_text('#ifndef _LUA_DEB_MULTIARCH_\n#define _LUA_DEB_MULTIARCH_\n#define DEB_HOST_MULTIARCH "powerpc-linux-gnuspe"\n#endif\n')
    obj=a.work/'lua-objects';obj.mkdir();files=[p for p in (src/'src').glob('*.c') if p.name not in ['lua.c','luac.c','print.c']]
    for f in files:run([cc,*cflags,'-fPIC','-DLUA_USE_POSIX','-DLUA_USE_DLOPEN','-I'+str(src/'src'),'-c',f,'-o',obj/(f.stem+'.o')],src)
    lib=stage/'usr/lib/liblua5.1.so.0';run([cc,*abi,'-shared','-Wl,-soname,liblua5.1.so.0','-o',lib,*sorted(obj.glob('*.o')),'-lm','-ldl'],src)
    (stage/'usr/lib/liblua5.1.so').symlink_to(lib.name);inc=stage/'usr/include/lua5.1';inc.mkdir()
    for f in ['lua.h','luaconf.h','lauxlib.h','lualib.h','lua5.1-deb-multiarch.h']:shutil.copy2(src/'src'/f,inc/f)
    pc=stage/'usr/lib/pkgconfig/lua.pc';pc.write_text('prefix=/usr\nlibdir=${prefix}/lib\nincludedir=${prefix}/include/lua5.1\nName: Lua\nDescription: Lua 5.1 target runtime\nVersion: 5.1.5\nLibs: -L${libdir} -llua5.1\nCflags: -I${includedir}\n');(pc.parent/'lua5.1.pc').symlink_to('lua.pc')
   elif name=='libxkbcommon':meson(src,name,['-Denable-docs=false','-Denable-tools=false','-Denable-wayland=false','-Denable-xkbregistry=false','-Denable-bash-completion=false'])
   elif name=='libxcvt':meson(src,name,[])
   elif name in ['libxkbfile','libfontenc','libxshmfence']:autotools(src,[])
   elif name=='libxfont':autotools(src,['--without-bzip2','--disable-devel-docs'])
   elif name=='xkeyboard-config':meson(src,name,['-Dcompat-rules=true'])
   elif name=='x11-xkb-utils':autotools(src/'xkbcomp',['--disable-selective-werror'])
   elif name=='xorg-server':meson(src,name,['-Dxorg=false','-Dxephyr=false','-Dxnest=false','-Dxwin=false','-Dxquartz=false','-Dxvfb=true','-Dglamor=false','-Dglx=false','-Ddri1=false','-Ddri2=false','-Ddri3=false','-Ddrm=false','-Dpciaccess=false','-Dudev=false','-Dudev_kms=false','-Dsystemd_logind=false','-Dxselinux=false','-Dsecure-rpc=false','-Ddocs=false','-Ddevel-docs=false','-Dxkb_dir=/usr/share/X11/xkb','-Dxkb_bin_dir=/usr/bin','-Dxkb_output_dir=/tmp','-Ddefault_font_path=/usr/share/fonts/X11/misc,built-ins'])
   elif name=='giflib':
    run(['make','-j'+str(a.jobs),'libgif.so','CC='+str(cc),'CFLAGS='+' '.join(cflags+['-std=gnu99','-fPIC'])],src)
    for f in src.glob('libgif.so*'):
     dest=stage/'usr/lib'/f.name
     if f.is_symlink():dest.symlink_to(os.readlink(f))
     else:shutil.copy2(f,dest)
    shutil.copy2(src/'gif_lib.h',stage/'usr/include/gif_lib.h')
   elif name=='libsndfile':cmakebuild(src,name,['-DBUILD_SHARED_LIBS=ON','-DENABLE_EXTERNAL_LIBS=OFF','-DENABLE_MPEG=OFF','-DBUILD_PROGRAMS=OFF','-DBUILD_EXAMPLES=OFF','-DBUILD_TESTING=OFF'])
   elif name=='libvncserver':cmakebuild(src,name,['-DWITH_GNUTLS=OFF','-DWITH_OPENSSL=OFF','-DWITH_GCRYPT=OFF','-DWITH_LZO=OFF','-DWITH_SDL=OFF','-DWITH_GTK=OFF','-DWITH_QT=OFF','-DWITH_SYSTEMD=OFF','-DWITH_LIBSSHTUNNEL=OFF','-DWITH_FFMPEG=OFF','-DWITH_SASL=OFF','-DWITH_EXAMPLES=OFF','-DWITH_TESTS=OFF','-DWITH_TIGHTVNC_FILETRANSFER=OFF'])
   elif name=='libmd':autotools(src,[])
   elif name=='dpkg':autotools(src,['--sysconfdir=/etc','--localstatedir=/var','--disable-nls','--disable-dselect','--disable-devel-docs','--without-libbz2','--without-liblzma','--without-libzstd','--without-libselinux','--with-deb-compressor=gzip'])
   elif name=='x11vnc':autotools(src,['--without-ssl','--without-crypt','--without-avahi'])
   else:raise ValueError(name)
   for f in (stage/'usr/lib').glob('*.la'):f.unlink()
   r['components'][name]={'status':'built','version':comp['version'],'notice_sha256':sha(notice)};save();print('BUILD_PASS',name,flush=True)
  r['elfs']={}
  for f in stage.rglob('*'):
   if f.is_file() and not f.is_symlink():
    with f.open('rb') as inp:data=inp.read(20)
    if data[:4]==b'\x7fELF':assert data[4:6]==b'\x01\x02' and data[18:20]==b'\x00\x14',f;r['elfs'][str(f.relative_to(stage))]=sha(f)
  r.update(status='built-not-runtime-tested',finished_unix=time.time());r.pop('active_component',None)
except Exception as e:r.update(status='failed',error=str(e),finished_unix=time.time());raise
finally:save()
print(r['status'],flush=True)
