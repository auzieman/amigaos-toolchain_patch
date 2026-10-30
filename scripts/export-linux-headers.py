#!/usr/bin/env python3
"""Export pinned Linux UAPI headers for the SPE bootstrap sysroot."""
import argparse,hashlib,json,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--project',type=Path,required=True);p.add_argument('--cache',type=Path,required=True)
p.add_argument('--work',type=Path,required=True);p.add_argument('--sysroot',type=Path,required=True)
a=p.parse_args();lock=json.loads((a.project/'profiles/debian-trixie.lock.json').read_text())
spec=next(f for f in lock['components']['linux']['files'] if '.orig.tar.' in f['filename'])
archive=a.cache/spec['filename']
if hashlib.sha256(archive.read_bytes()).hexdigest()!=spec['sha256']:p.error('kernel archive mismatch')
a.work.mkdir(parents=True,exist_ok=False)
root='linux-6.12.113';names=['Makefile','Kbuild','Kconfig','include','scripts','arch/powerpc','arch/Kconfig']
receipt={'status':'started','source_sha256':spec['sha256'],'scope':'upstream UAPI subset; no Debian packaging/board patch changes UAPI here','commands':[]}
with (a.work/'build.log').open('w') as log:
 def run(cmd):receipt['commands'].append(cmd);subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
 try:
  run(['tar','-xJf',str(archive),'-C',str(a.work)]+[root+'/'+n for n in names])
  run(['make','-C',str(a.work/root),'ARCH=powerpc','headers_install','INSTALL_HDR_PATH='+str(a.sysroot/'usr')])
  receipt['headers']={str(f.relative_to(a.sysroot)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((a.sysroot/'usr/include').rglob('*.h'))}
  receipt['status']='exported'
 except Exception as exc:receipt['status']='failed';receipt['error']=str(exc);raise
 finally:(a.work/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'])
