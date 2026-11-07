from pathlib import Path
import difflib,subprocess,json
w=Path('/srv/data1/tabor-build/linux-live-001/work/gcc14-spe-port-20261107-001');m=w/'modern'
p=m/'gcc/config/powerpcspe/sysv4.h';a=p.read_text();old='/* Header files should be C++ aware in general.  */\n#undef  NO_IMPLICIT_EXTERN_C\n#define NO_IMPLICIT_EXTERN_C\n\n';assert old in a;b=a.replace(old,'',1);p.write_text(b)
(w/'0004-remove-obsolete-extern-c-switch.patch').write_text(''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/gcc/config/powerpcspe/sysv4.h',tofile='b/gcc/config/powerpcspe/sysv4.h')))
args=['docker','run','-d','--name','tabor-gcc14-spe-stage1-004','--cpus=4','--memory=6g','--network=none','--entrypoint','/bin/sh','-v',str(w)+':/work','sha256:2781e11839beffa351f8c411d71b7e2bd1ae0336d24c60b407778c3350dd9da0','-c','cd /work/build-stage1 && make -k -j4 all-gcc > /work/build-stage1-004.log 2>&1']
print(subprocess.check_output(args,text=True).strip());(w/'launch-004.json').write_text(json.dumps({'command':args,'qualification':'diagnostic only; obsolete header switch removed as in modern rs6000'},indent=2)+'\n')
