from pathlib import Path
import subprocess,json
b=Path('/srv/data1/tabor-build/linux-live-001');w=b/'work/gfx-write-20261109-001';w.mkdir(exist_ok=True)
(w/'gfx-write.c').write_bytes(Path('/home/owner/gfx-write-20261109.c').read_bytes())
k=b/'work/kmscube-build-20261109-001'
cmd=['docker','run','--rm','--name','tabor-gfx-write-20261109-001','--cpus=1','--memory=1g','--network=none','-v',str(w)+':/test','-v',str(k/'stage')+':/deps:ro','-v',str(b/'tools/cxx-reference-002')+':/tools:ro','-v',str(b/'sysroot')+':/sysroot:ro','--entrypoint','sh','sha256:0434a7f8dfeec379cd81d334e2a2eaa02208653e494d56334bcc486950be8a49','-c','/tools/bin/powerpc-linux-gnuspe-gcc --sysroot=/sysroot -mcpu=8548 -mabi=spe -mspe -mfloat-gprs=double -mlong-double-128 -O2 -I/deps/usr/include/libdrm /test/gfx-write.c -L/deps/usr/lib/powerpc-linux-gnuspe -Wl,-rpath-link,/deps/usr/lib/powerpc-linux-gnuspe -ldrm_amdgpu -ldrm -o /test/gfx-write']
r=subprocess.run(cmd,capture_output=True,text=True);(w/'build.log').write_text(r.stdout+r.stderr);(w/'launch.json').write_text(json.dumps({'argv':cmd,'exit':r.returncode},indent=2));print(r.stdout,r.stderr);r.check_returncode()
