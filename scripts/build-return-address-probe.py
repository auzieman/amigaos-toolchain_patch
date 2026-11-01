#!/usr/bin/env python3
"""Compile a small SPE return-address flag matrix; execution is a separate gate."""
import argparse, hashlib, json, subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for name in ['project','tools','sysroot','output']:
 p.add_argument('--'+name,type=Path,required=True)
p.add_argument('--image-id',required=True)
a=p.parse_args(); a.output.mkdir(exist_ok=False)
cc=a.tools/'bin/powerpc-linux-gnuspe-gcc'
objdump=a.tools/'bin/powerpc-linux-gnuspe-objdump'
source=a.project/'bench/spe-return-address.c'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
base=['--sysroot='+str(a.sysroot),'-O2','-g','-mcpu=8548','-mabi=spe',
      '-mspe','-mfloat-gprs=double','-mlong-double-128']
modes={'plain':[], 'protected':['-fstack-protector-strong','-fexceptions'],
 'frame':['-fstack-protector-strong','-fexceptions','-fno-omit-frame-pointer'],
 'pic':['-fpic','-fstack-protector-strong','-fexceptions'],
 'pic-plain':['-fpic','-fno-stack-protector','-fexceptions'],
 'pic-frame':['-fpic','-fstack-protector-strong','-fexceptions','-fno-omit-frame-pointer']}
r={'status':'building','source_sha256':sha(source),'image_id':a.image_id,
   'compiler_sha256':sha(cc.resolve()),'flags':base,'modes':{},'executed':False}
try:
 for mode,extra in modes.items():
  out=a.output/('probe-'+mode)
  command=[str(cc),*base,*extra,str(source),'-o',str(out),'-ldl']
  subprocess.run(command,check=True)
  asm=subprocess.check_output([str(objdump),'-d',str(out)])
  dis=out.with_suffix('.dis');dis.write_bytes(asm)
  r['modes'][mode]={'command':command,'sha256':sha(out),'disassembly_sha256':sha(dis)}
 r['status']='built-not-executed'
except Exception as exc:
 r.update(status='failed',error=str(exc)); raise
finally:
 (a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
