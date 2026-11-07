from pathlib import Path
import subprocess,difflib,json
w=Path('/srv/data1/tabor-build/linux-live-001/work/gcc14-spe-port-20261107-001'); m=w/'modern'
p=w.parent/'gcc14-spe-foundation-20261107-001/debian-source/debian/patches/gcc-gfdl-build.diff'
subprocess.run(['patch','-p2','--batch','--forward'],cwd=m,input=p.read_bytes(),check=True)
patch=''
for rel,old,new in [('gcc/config.gcc',' dbxelf.h elfos.h gnu-user.h freebsd-spec.h powerpcspe/sysv4.h',' elfos.h gnu-user.h freebsd-spec.h powerpcspe/sysv4.h'),('gcc/config/powerpcspe/powerpcspe.h','#define DBX_REGISTER_NUMBER(REGNO)','#define DEBUGGER_REGNO(REGNO)')]:
 f=m/rel;a=f.read_text();assert old in a;b=a.replace(old,new,1);f.write_text(b);patch+=''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
(w/'0003-modern-debug-interface.patch').write_text(patch)
(w/'debian-gcc-gfdl-build.diff').write_bytes(p.read_bytes())
image='sha256:2781e11839beffa351f8c411d71b7e2bd1ae0336d24c60b407778c3350dd9da0'
args=['docker','run','-d','--name','tabor-gcc14-spe-stage1-003','--cpus=4','--memory=6g','--network=none','--entrypoint','/bin/sh','-v',str(w)+':/work',image,'-c','cd /work/build-stage1 && make -k -j4 all-gcc > /work/build-stage1-003.log 2>&1']
cid=subprocess.check_output(args,text=True).strip();(w/'launch-003.json').write_text(json.dumps({'container':cid,'command':args,'qualification':'diagnostic compiler bootstrap only','changes':['Debian gcc-gfdl-build.diff at -p2','remove obsolete Linux SPE STABS header','rename debugger hook; preserve SPE register mapping function']},indent=2)+'\n');print(cid)
