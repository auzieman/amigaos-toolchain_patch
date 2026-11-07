from pathlib import Path
import shutil,hashlib,json,difflib,subprocess
w=Path('/srv/data1/tabor-build/linux-live-001/work/gcc14-spe-port-20261107-001');old=w/'legacy';new=w/'modern'
roots=['gcc/config/powerpcspe','gcc/common/config/powerpcspe']
files=[p for root in roots for p in (old/root).rglob('*') if p.is_file()]
renames={p.name:p.stem+'.cc' for p in files if p.suffix=='.c'}
manifest=[]
for p in files:
 rel=p.relative_to(old);dest=rel.with_suffix('.cc') if p.suffix=='.c' else rel
 data=p.read_bytes();result=data
 for a,b in renames.items():result=result.replace(a.encode(),b.encode())
 out=new/dest;assert not out.exists();out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(result)
 manifest.append({'source':str(rel),'destination':str(dest),'source_sha256':hashlib.sha256(data).hexdigest(),'output_sha256':hashlib.sha256(result).hexdigest()})
(w/'imports.json').write_text(json.dumps({'reference':'GNU GCC8.5.0; official archive pin in profiles/toolchain-bootstrap.json','transform':'Rename backend C++ implementation .c suffixes and their filename references to .cc for GCC14 build rules; preserve other bytes/notices','files':manifest},indent=2)+'\n')
p=new/'gcc/config.gcc';a=p.read_text();s=a
# Exempt only Linux SPE from the removed-target rejection; other SPE targets remain unsupported.
pos=s.index(' | powerpc*-*-*spe*');start=s.rfind('case ${target} in',0,pos);assert start>=0
start+=len('case ${target} in');s=s[:start]+'\npowerpc*-*-linux*spe*) ;;'+s[start:]
o=(old/'gcc/config.gcc').read_text();start=o.index('powerpc*-*-*spe*)\n\tcpu_type=powerpcspe');end=o.index('\n\t;;',start)+len('\n\t;;')
block=o[start:end].replace('powerpc*-*-*spe*)','powerpc*-*-linux*spe*)')
needle='powerpc*-*-*)\n\tcpu_type=rs6000';assert needle in s;s=s.replace(needle,block+'\n'+needle,1)
start=o.index('powerpc*-*-linux*spe*)\n\ttm_file=');end=o.index('\n\t;;',start)+len('\n\t;;');block=o[start:end]
needle='powerpc*-*-linux*)\n';assert needle in s;s=s.replace(needle,block+'\n'+needle,1)
p.write_text(s)
patch=''.join(difflib.unified_diff(a.splitlines(True),s.splitlines(True),fromfile='a/gcc/config.gcc',tofile='b/gcc/config.gcc'))
(w/'0001-register-linux-powerpcspe.patch').write_text(patch)
build=w/'build-stage1';build.mkdir(exist_ok=False)
image='sha256:2781e11839beffa351f8c411d71b7e2bd1ae0336d24c60b407778c3350dd9da0'
configure=['/work/modern/configure','--target=powerpc-linux-gnuspe','--prefix=/opt/tabor-sdk-candidate','--enable-languages=c','--disable-bootstrap','--disable-multilib','--disable-nls','--without-headers','--disable-shared','--disable-threads','--disable-libsanitizer','--disable-libquadmath','--disable-libgomp','--disable-libatomic','--enable-checking=release','--with-cpu=8548','--with-long-double-128','--enable-e500-double','--with-as=/usr/bin/powerpc-linux-gnu-as','--with-ld=/usr/bin/powerpc-linux-gnu-ld']
import shlex
command='set -eu; cd /work/build-stage1; '+shlex.join(configure)+' > /work/configure-stage1.log 2>&1; make -j4 all-gcc > /work/build-stage1.log 2>&1'
args=['docker','run','-d','--name','tabor-gcc14-spe-stage1-001','--cpus=4','--memory=6g','--network=none','--entrypoint','/bin/sh','-v',str(w)+':/work',image,'-c',command]
cid=subprocess.check_output(args,text=True).strip();(w/'launch.json').write_text(json.dumps({'container':cid,'command':args,'configure':configure,'phase':'compiler-only bootstrap; not installed or ABI accepted','legacy_sdk_unchanged':True,'imported_files':len(files),'target_integration_patch_sha256':hashlib.sha256(patch.encode()).hexdigest()},indent=2)+'\n');print('Launched compiler-only stage:',cid,'imported files:',len(files))
