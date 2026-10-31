#!/usr/bin/env python3
"""Link an SPE X11 protocol probe and stage its verified shared-library closure."""
import argparse,hashlib,json,re,shutil,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for n in ['project','tools','sysroot','stage','output']:p.add_argument('--'+n,type=Path,required=True)
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);payload=a.output/'payload';payload.mkdir();(payload/'lib').mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cc=a.tools/'bin/powerpc-linux-gnuspe-gcc';source=a.project/'bench/x11-client-check.c';binary=payload/'x11-client-check'
flags=['--sysroot='+str(a.sysroot),'-mcpu=8548','-mabi=spe','-mspe','-mfloat-gprs=double','-mlong-double-128','-O2','-I'+str(a.stage/'usr/include'),'-L'+str(a.stage/'usr/lib'),'-Wl,-rpath-link,'+str(a.stage/'usr/lib')]
r={'status':'started','source_sha256':sha(source),'flags':flags,'libraries':{},'physical_boot':False,'target_Xorg_tested':False}
def inspect(f):
 data=f.read_bytes();assert data[:6]==b'\x7fELF\x01\x02' and data[18:20]==b'\x00\x14',f
 return subprocess.check_output(['powerpc-linux-gnu-readelf','-ld',str(f)],text=True)
try:
 with (a.output/'build.log').open('w') as log:
  subprocess.run([str(cc),*flags,str(source),'-lXrender','-lXrandr','-lXfixes','-lX11','-lxcb','-o',str(binary)],stdout=log,stderr=subprocess.STDOUT,check=True)
 data=inspect(binary);assert 'Requesting program interpreter: /lib/ld.so.1]' in data
 pending=re.findall(r'\(NEEDED\).*\[([^\]]+)\]',data);seen=set()
 while pending:
  name=pending.pop()
  if name in seen:continue
  seen.add(name);assert Path(name).name==name
  f=next((p.resolve() for p in [a.stage/'usr/lib'/name,a.sysroot/'lib'/name,a.sysroot/'usr/lib'/name] if p.is_file()),None)
  assert f and any(f.is_relative_to(p.resolve()) for p in [a.stage,a.sysroot]),name
  data=inspect(f);r['libraries'][name]={'path':str(f),'sha256':sha(f)}
  subprocess.run(['powerpc-linux-gnu-strip','--strip-unneeded','-o',str(payload/'lib'/name),str(f)],check=True)
  pending+=re.findall(r'\(NEEDED\).*\[([^\]]+)\]',data)
 r['files']={str(f.relative_to(payload)):sha(f) for f in payload.rglob('*') if f.is_file()};r['status']='probe-linked-closure-checked-not-executed'
except Exception as e:r.update(status='failed',error=str(e));raise
finally:(a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
print(r['status'])
