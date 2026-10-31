#!/usr/bin/env python3
"""Cross-build software X11 EFL/E/Terminology with separate native generators."""
import argparse,hashlib,json,os,shutil,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for n in ['project','cache','tools','sysroot','base-stage','work']:p.add_argument('--'+n,type=Path,required=True)
p.add_argument('--image-id',required=True);p.add_argument('--jobs',type=int,default=4);p.add_argument('--components',default='')
a=p.parse_args();assert 1<=a.jobs<=8;a.work.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();stage=a.work/'stage';shutil.copytree(a.base_stage,stage,symlinks=True)
lockpath=a.project/'profiles/desktop-seeds.lock.json';lock=json.loads(lockpath.read_text())
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
 build=a.work/(name+'-build');run(['cmake','-S',src,'-B',build,'-G','Ninja','-DCMAKE_TOOLCHAIN_FILE='+str(cmake),'-DCMAKE_INSTALL_PREFIX=/usr','-DCMAKE_INSTALL_LIBDIR=lib','-DCMAKE_BUILD_TYPE=Release',*opts],a.work);run(['cmake','--build',build,'--parallel',a.jobs],a.work)
 old=env.get('DESTDIR');env['DESTDIR']=str(stage)
 try:run(['cmake','--install',build],a.work)
 finally:
  if old is None:env.pop('DESTDIR',None)
  else:env['DESTDIR']=old
try:
 with (a.work/'build.log').open('w') as log:
  selected=a.components.split(',') if a.components else ['efl','e17','terminology']
  for name in selected:
   comp=lock['components'][name];r['active_component']=name;save();print('BUILD_START',name,flush=True)
   for f in comp['files']:
    file=a.cache/f['filename'];assert file.stat().st_size==f['size'] and sha(file)==f['sha256'],file
   src=a.work/(name+'-source');run(['dpkg-source','--no-check','-x',a.cache/comp['dsc'],src],a.work)
   notice=src/'debian/copyright';assert notice.is_file();shutil.copy2(notice,a.work/(name+'-copyright'))
   if name=='efl':
    opts=json.loads((a.project/'profiles/images/efl-software-session.json').read_text())['options']
    args=[]
    for k,v in opts.items():
     value=str(v).lower() if isinstance(v,bool) else ','.join(v) if isinstance(v,list) else str(v)
     args.append('-D'+k+'='+value)
    meson(src,name,args)
   elif name=='e17':
    off=['nls','pam','libexif','elput','device-udev','mount-udisks','mount-eeze','wl','xwayland','systemd','bluez5','connman','backlight','battery','convertible','cpufreq','geolocation','polkit','mixer','music-control','packagekit','temperature','gesture-recognition','procstats']
    meson(src,name,['-D'+n+'=false' for n in off]+['-Dedje-cc=/usr/bin/edje_cc','-Deet=/usr/bin/eet','-Deldbus-codegen=/usr/bin/eldbus-codegen'])
   elif name=='terminology':meson(src,name,['-Dnls=false','-Dtests=false','-Ddocs=false'])
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
