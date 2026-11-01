#!/usr/bin/env python3
"""Compile one probe against real package headers/library and verify .deb payload identity."""
import argparse,hashlib,json,shutil,subprocess,tarfile
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for n in ['project','tools','sysroot','package-build','output']:p.add_argument('--'+n,type=Path,required=True)
for n in ['binary-package','header-package','library','source','image-id']:p.add_argument('--'+n,required=True)
a=p.parse_args();a.output.mkdir(exist_ok=False)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
b=json.loads((a.package_build/'receipt.json').read_text());assert b['status']=='debian-packages-built-not-target-installed'
package=next(n for n in b['packages'] if n.startswith(a.binary_package+'_') and n.endswith('.deb'))
deb=a.package_build/package;assert sha(deb)==b['packages'][package]['sha256']
stage=a.package_build/'source/debian'/a.binary_package
library=(stage/'usr/lib/powerpc-linux-gnuspe'/a.library).resolve();assert library.is_relative_to(stage.resolve())
rel=str(library.relative_to(stage.resolve()));digest=sha(library);found=False
proc=subprocess.Popen(['dpkg-deb','--fsys-tarfile',str(deb)],stdout=subprocess.PIPE)
with tarfile.open(fileobj=proc.stdout,mode='r|') as tar:
 for m in tar:
  if m.isfile() and m.name.lstrip('./')==rel:
   assert hashlib.sha256(tar.extractfile(m).read()).hexdigest()==digest;found=True
assert proc.wait()==0 and found
source=a.project/a.source; cc=a.tools/'bin/powerpc-linux-gnuspe-gcc'
flags=['--sysroot='+str(a.sysroot),'-O2','-mcpu=8548','-mabi=spe','-mspe','-mfloat-gprs=double','-mlong-double-128']
command=[str(cc),*flags,'-I'+str(a.package_build/'source/debian'/a.header_package/'usr/include'),str(source),str(library),'-o',str(a.output/'probe')]
subprocess.run(command,check=True)
shutil.copyfile(library,a.output/a.library)
elf=(a.output/'probe').read_bytes();assert elf[:6]==b'\x7fELF\x01\x02'
r={'status':'probe-built-not-executed','command':command,'image_id':a.image_id,
   'source_sha256':sha(source),'package':package,'package_sha256':sha(deb),
   'package_build_receipt_sha256':sha(a.package_build/'receipt.json'),
   'files':{n:sha(a.output/n) for n in ['probe',a.library]}}
(a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'])
