#!/usr/bin/env python3
"""Build a source-pinned SPE Evas isolation probe with target-only pkg-config paths."""
import argparse,hashlib,json,os,shlex,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for n in ['project','stage','tools','sysroot','output']:p.add_argument('--'+n,type=Path,required=True)
p.add_argument('--image-id',required=True);a=p.parse_args();a.output.mkdir(exist_ok=False)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
env={**os.environ,'PKG_CONFIG_SYSROOT_DIR':str(a.stage),'PKG_CONFIG_LIBDIR':':'.join([str(a.stage/'usr/lib/pkgconfig'),str(a.stage/'usr/share/pkgconfig'),'/usr/share/pkgconfig']),'PKG_CONFIG_PATH':''}
src=a.project/'bench/evas-pixel-probe.c';cc=a.tools/'bin/powerpc-linux-gnuspe-gcc'
pc=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','ecore-evas','ecore-x','edje','x11'],env=env,text=True))
cmd=[str(cc),'--sysroot='+str(a.sysroot),'-mcpu=8548','-mabi=spe','-mspe','-mfloat-gprs=double','-mlong-double-128','-O2',str(src),'-o',str(a.output/'probe'),'-Wl,-rpath-link,'+str(a.stage/'usr/lib'),*pc]
r={'status':'started','image_id':a.image_id,'source_sha256':sha(src),'compiler_sha256':sha(cc),'command':cmd,'physical_boot':False}
try:
 subprocess.run(cmd,check=True);assert (a.output/'probe').read_bytes()[:6]==b'\x7fELF\x01\x02';r.update(status='compiled-not-executed',binary_sha256=sha(a.output/'probe'))
except Exception as e:r.update(status='failed',error=str(e));raise
finally:(a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
print(r['status'])
