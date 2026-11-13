"""R730-only: retain completion and separately qualify staged GCC14 runtimes."""
from pathlib import Path
import hashlib,json,subprocess,os
w=Path('/srv/data1/tabor-build/linux-live-001/work/gcc14-sdk-20261108-001')
inputs=Path('/home/owner/gcc14-sdk-20261108')
receipt={'status':'waiting-for-build','target_installed':False,'debian_consumers_started':False,'hardware_accessed':False}
def save(): (w/'qualification-002.json').write_text(json.dumps(receipt,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save()
try:
 code=int(subprocess.check_output(['docker','wait','tabor-gcc14-sdk-install-002'],text=True).strip())
 receipt['build_exit']=code
 if code: raise RuntimeError('SDK build failed; inspect result.exit and build logs')
 prefix='/fresh/stage-002/opt/tabor-gcc14-candidate'
 flags='--sysroot='+prefix+'/sysroot -mcpu=8548 -mabi=spe -mspe -mfloat-gprs=double -mlong-double-128 -O2 -pthread'
 command='set -eu; mkdir /fresh/probes-002; '+prefix+'/bin/powerpc-linux-gnuspe-gcc '+flags+' /inputs/spe-abi-smoke.c -lm -o /fresh/probes-002/spe-abi; '+prefix+'/bin/powerpc-linux-gnuspe-g++ '+flags+' /inputs/spe-cxx-smoke.cpp -o /fresh/probes-002/spe-cxx'
 image='sha256:2781e11839beffa351f8c411d71b7e2bd1ae0336d24c60b407778c3350dd9da0'
 with (w/'probe-compile-002.log').open('w') as log:
  subprocess.run(['docker','run','--rm','--name','tabor-gcc14-sdk-probes-002','--cpus=1','--memory=2g','--pids-limit=128','--network=none','--entrypoint','/bin/sh','-v',str(w)+':/fresh','-v',str(inputs)+':/inputs:ro',image,'-c',command],stdout=log,stderr=subprocess.STDOUT,check=True)
 root=w/'stage-002/opt/tabor-gcc14-candidate'
 libs=[root/'sysroot/lib',root/'sysroot/usr/lib',root/'powerpc-linux-gnuspe/lib',root/'lib']
 receipt['probes']={}
 for name,args in [('spe-abi',['--cli']),('spe-cxx',['--cli'])]:
  exe=w/'probes-002'/name
  header=subprocess.check_output(['readelf','-h',str(exe)],text=True)
  assert 'ELF32' in header and 'big endian' in header and 'PowerPC' in header
  p=subprocess.run(['timeout','90','qemu-ppc','-cpu','e500v2','-L',str(root/'sysroot'),str(root/'sysroot/lib/ld.so.1'),'--library-path',':'.join(map(str,libs)),str(exe),*args],capture_output=True,text=True)
  (w/(name+'-qemu-002.log')).write_text(p.stdout+p.stderr)
  receipt['probes'][name]={'sha256':sha(exe),'exit':p.returncode}
 receipt['status']='runtime-probes-passed-not-promoted' if all(x['exit']==0 for x in receipt['probes'].values()) else 'runtime-probes-have-failures-not-promoted'
 receipt['limitations']=['QEMU fenv discrepancy requires retained native comparison; do not weaken semantics','No Debian SDK/runtime package or clean sbuild-root acceptance yet','No physical execution or GPU changes']
except Exception as e:
 receipt['status']='failed-not-promoted';receipt['error']=str(e)
finally: save()
