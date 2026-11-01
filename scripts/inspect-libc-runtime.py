#!/usr/bin/env python3
"""Match staged ELF runtime files to the actual Debian libc6 payload."""
import argparse, hashlib, json, subprocess, tarfile
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build',type=Path,required=True);a=p.parse_args()
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
r=json.loads((a.build/'receipt.json').read_text());assert r['status']=='debian-packages-built-not-target-installed'
name=next(n for n in r['packages'] if n.startswith('libc6_') and n.endswith('.deb'))
package=a.build/name;assert sha(package)==r['packages'][name]['sha256']
expected={n:sha(a.build/'source/debian/libc6/usr/lib/powerpc-linux-gnuspe'/n) for n in ['ld.so.1','libc.so.6','libm.so.6']}
proc=subprocess.Popen(['dpkg-deb','--fsys-tarfile',str(package)],stdout=subprocess.PIPE)
found={}
with tarfile.open(fileobj=proc.stdout,mode='r|') as tar:
 for m in tar:
  n=Path(m.name).name
  if m.isfile() and n in expected and m.name.lstrip('./')=='usr/lib/powerpc-linux-gnuspe/'+n:
   data=tar.extractfile(m).read();assert data[:6]==b'\x7fELF\x01\x02'
   found[n]=hashlib.sha256(data).hexdigest()
assert proc.wait()==0 and found==expected
result={'status':'package-runtime-match','package':name,'package_sha256':sha(package),
        'build_receipt_sha256':sha(a.build/'receipt.json'),'files_sha256':found}
(a.build/'runtime-package-proof.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['status'])
