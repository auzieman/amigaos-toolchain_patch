#!/usr/bin/env python3
"""Compile a static reference C++ runtime probe and retain bounded e500v2 execution."""
import argparse,hashlib,json,re,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for name in ['project','tools','sysroot','kernel','output']:p.add_argument('--'+name,type=Path,required=True)
p.add_argument('--image-id',required=True)
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
source=a.project/'bench/spe-cxx-smoke.cpp';binary=a.output/'cxx-init'
flags=['--sysroot='+str(a.sysroot),'-mcpu=8548','-mabi=spe','-mspe',
       '-mfloat-gprs=double','-mlong-double-128','-std=c++17','-O2','-g0','-static','-pthread',
       '-Wl,-u,pthread_create,-u,pthread_join,-u,pthread_detach,-u,pthread_once,-u,pthread_cancel']
r={'status':'started','image_id':a.image_id,'source_sha256':sha(source),
   'flags':flags,'physical_boot':False,'full_spe_abi_validated':False,
   'scope':'reference GCC8 C++ exceptions/RAII, thread TLS and uint32 atomics only'}
try:
 cc=a.tools/'bin/powerpc-linux-gnuspe-g++'
 r['compiler_version']=subprocess.check_output([str(cc),'--version'],text=True)
 with (a.output/'build.log').open('w') as log:
  subprocess.run([str(cc),*flags,str(source),'-o',str(binary)],stdout=log,stderr=subprocess.STDOUT,check=True)
 r['binary_sha256']=sha(binary)
 dis=subprocess.check_output(['powerpc-linux-gnu-objdump','-d',str(binary)])
 (a.output/'disassembly.txt').write_bytes(dis)
 r['spe_double_add_present']=bool(re.search(rb'\befdadd\b',dis))
 assert r['spe_double_add_present']
 subprocess.run([sys.executable,str(a.project/'scripts/qemu-boot-smoke.py'),
  '--kernel',str(a.kernel),'--init-binary',str(binary),'--output',str(a.output/'boot'),
  '--timeout','20','--image-id',a.image_id],check=False)
 boot=json.loads((a.output/'boot/receipt.json').read_text());data=(a.output/'boot/serial.log').read_bytes().replace(b'\r',b'')
 checks={n.decode():v.decode() for n,v in re.findall(rb'^CXX_TEST (\w+) (PASS|FAIL)$',data,re.M)}
 r.update(check_status=checks,serial_sha256=boot['serial_sha256'],boot_status=boot['status'],panic_seen=boot['panic_seen'])
 assert boot['status']=='passed' and not boot['panic_seen']
 assert set(checks)=={'long_double_128','exception_unwind','thread_tls','atomic_u32'}
 assert all(v=='PASS' for v in checks.values()) and b'CXX_SMOKE_DONE failures=0' in data
 r['status']='passed-basic-CXX-reference-checks'
except Exception as error:
 r.update(status='failed',error=str(error));raise
finally:(a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
