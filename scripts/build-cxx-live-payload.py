#!/usr/bin/env python3
"""Stage a shared C++ CLI probe with a recursively checked PPC/SPE runtime closure."""
import argparse,hashlib,json,re,shutil,subprocess,struct
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for n in ['project','tools','sysroot','output']:p.add_argument('--'+n,type=Path,required=True)
p.add_argument('--image-id',required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
cc=a.tools/'bin/powerpc-linux-gnuspe-g++';root=a.output/'payload';(root/'bin').mkdir(parents=True)
source=a.project/'bench/spe-cxx-smoke.cpp';binary=root/'bin/spe-cxx-check'
flags=['--sysroot='+str(a.sysroot),'-mcpu=8548','-mabi=spe','-mspe','-mfloat-gprs=double',
       '-mlong-double-128','-std=c++17','-O2','-g0','-pthread']
r={'status':'started','image_id':a.image_id,'source_sha256':sha(source),'flags':flags,
   'physical_boot':False,'full_spe_abi_validated':False,'library_inputs':{}}
def inspect(file):
 elf=file.read_bytes();assert elf[:6]==b'\x7fELF\x01\x02' and struct.unpack_from('>H',elf,18)[0]==20,file
 return subprocess.check_output(['powerpc-linux-gnu-readelf','-ld',str(file)],text=True)
def resolve(name):
 assert Path(name).name==name
 found=subprocess.check_output([str(cc),'-print-file-name='+name],text=True).strip()
 candidates=[Path(found),a.sysroot/'lib'/name,a.sysroot/'usr/lib'/name]
 for f in candidates:
  if f.is_file():
   f=f.resolve()
   assert any(f.is_relative_to(x.resolve()) for x in [a.tools,a.sysroot]),f
   return f
 raise RuntimeError('Unresolved target library: '+name)
try:
 with (a.output/'build.log').open('w') as log:
  subprocess.run([str(cc),*flags,str(source),'-o',str(binary)],stdout=log,stderr=subprocess.STDOUT,check=True)
 data=inspect(binary);interp=re.search(r'Requesting program interpreter: ([^\]]+)',data);assert interp
 path=interp[1];assert path=='/lib/ld.so.1',path
 pending=[Path(path).name]+re.findall(r'\(NEEDED\).*\[([^\]]+)\]',data);seen=set()
 while pending:
  name=pending.pop()
  if name in seen:continue
  seen.add(name);file=resolve(name);data=inspect(file)
  r['library_inputs'][name]={'path':str(file),'sha256':sha(file)}
  dest=root/'lib'/name;dest.parent.mkdir(exist_ok=True)
  subprocess.run(['powerpc-linux-gnu-strip','--strip-unneeded','-o',str(dest),str(file)],check=True)
  pending+=re.findall(r'\(NEEDED\).*\[([^\]]+)\]',data)
 files=[{'path':str(f.relative_to(root)),'sha256':sha(f),'mode':0o755} for f in sorted(root.rglob('*')) if f.is_file()]
 (a.output/'payload-manifest.json').write_text(json.dumps({'files':files},indent=2)+'\n')
 r.update(status='shared-CXX-payload-built-not-executed',files=files,interpreter=path,
          manifest_sha256=sha(a.output/'payload-manifest.json'))
except Exception as error:r.update(status='failed',error=str(error));raise
finally:(a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
print(r['status'])
