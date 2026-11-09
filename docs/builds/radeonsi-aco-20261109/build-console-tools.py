from pathlib import Path
import subprocess,json,hashlib
b=Path('/srv/data1/tabor-build/linux-live-001');old=b/'work/test-tools-20261109-001';w=b/'work/render-tools-20261109-001';w.mkdir(exist_ok=False)
for name in ['busybox-1.37.0','busybox-obj']:subprocess.run(['cp','-a','--reflink=auto',str(old/name),str(w/name)],check=True)
p=w/'busybox-obj/.config';s=p.read_text()
for name in ['CHROOT','SETSID','TIMEOUT','CHVT']:
 s=s.replace('# CONFIG_'+name+' is not set','CONFIG_'+name+'=y')
p.write_text(s)
cmd=['docker','run','-d','--name','tabor-render-tools-20261109-001','--cpus=2','--memory=2g','--network=none','--entrypoint','/bin/sh','-v',str(w)+':/work','-v',str(b/'tools')+':/tools:ro','-v',str(b/'sysroot')+':/sysroot:ro','sha256:2781e11839beffa351f8c411d71b7e2bd1ae0336d24c60b407778c3350dd9da0','-c','make -C /work/busybox-1.37.0 O=/work/busybox-obj CROSS_COMPILE=/tools/reference-001/bin/powerpc-linux-gnuspe- "CONFIG_EXTRA_CFLAGS=--sysroot=/sysroot -isystem /sysroot/usr/include -B/sysroot/usr/lib/ -mcpu=8548 -mabi=spe -mspe -mfloat-gprs=double -mlong-double-128" "CONFIG_EXTRA_LDFLAGS=--sysroot=/sysroot" oldconfig > /work/configure.log 2>&1 && make -C /work/busybox-1.37.0 O=/work/busybox-obj CROSS_COMPILE=/tools/reference-001/bin/powerpc-linux-gnuspe- "CONFIG_EXTRA_CFLAGS=--sysroot=/sysroot -isystem /sysroot/usr/include -B/sysroot/usr/lib/ -mcpu=8548 -mabi=spe -mspe -mfloat-gprs=double -mlong-double-128" "CONFIG_EXTRA_LDFLAGS=--sysroot=/sysroot" -j2 > /work/build.log 2>&1; r=$?; echo "$r" > /work/result.exit; exit "$r"']
r=subprocess.run(cmd,capture_output=True,text=True);(w/'launch.json').write_text(json.dumps({'argv':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n');print(r.stdout,r.stderr);r.check_returncode()
