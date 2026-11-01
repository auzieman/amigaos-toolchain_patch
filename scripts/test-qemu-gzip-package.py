#!/usr/bin/env python3
"""Check the actual gzip .deb payload against libc004 in an existing QEMU guest."""
import argparse,hashlib,json,shlex,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for n in ['remote-helper','identity','known-hosts','output']:p.add_argument('--'+n,type=Path,required=True)
p.add_argument('--build',required=True);p.add_argument('--port',type=int,required=True)
a=p.parse_args();a.output.mkdir(exist_ok=False)
sha=lambda b:hashlib.sha256(b).hexdigest()
ssh=['ssh','-F','/dev/null','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(a.known_hosts),'-i',str(a.identity),'-p',str(a.port),'tabor@127.0.0.1']
def fetch(command):return subprocess.check_output(['python3',str(a.remote_helper),command],timeout=45)
def guest(args,data=None):return subprocess.run(ssh+[shlex.join(args)],input=data,capture_output=True,timeout=60,check=True).stdout
r={'status':'started','scope':'Actual package payload, private libc004, existing system-QEMU; not target installation or physical acceptance','recipe_sha256':sha(Path(__file__).read_bytes())}
try:
 raw=fetch('cat '+shlex.quote(a.build+'/receipt.json'));build=json.loads(raw);assert build['status']=='debian-packages-built-not-target-installed'
 name=next(n for n in build['packages'] if n.startswith('gzip_') and n.endswith('.deb'));path=a.build+'/'+name
 assert fetch('sha256sum '+shlex.quote(path)).decode().split()[0]==build['packages'][name]['sha256']
 binary=fetch('dpkg-deb --fsys-tarfile '+shlex.quote(path)+' | tar -xOf - ./usr/bin/gzip');assert binary[:6]==b'\x7fELF\x01\x02'
 dest='/home/tabor/gzip-package-004';guest(['mkdir','-p',dest])
 subprocess.run(ssh+['cat > '+shlex.quote(dest+'/gzip')+' && chmod 755 '+shlex.quote(dest+'/gzip')],input=binary,check=True,timeout=30)
 assert sha(guest(['cat',dest+'/gzip']))==sha(binary)
 loader=['/home/tabor/glibc-stage2-004/ld.so.1','--library-path','/home/tabor/glibc-stage2-004:/lib:/usr/lib']
 maps=guest(loader+['--list',dest+'/gzip']).decode();assert '/home/tabor/glibc-stage2-004/libc.so.6' in maps
 (a.output/'loader-map.log').write_text(maps)
 payload=(b'Tabor SPE Debian gzip package runtime check.\n'*1536)
 compressed=guest(loader+[dest+'/gzip','-n','-c'],payload)
 assert compressed[:3]==b'\x1f\x8b\x08'
 assert guest(loader+[dest+'/gzip','-d','-c'],compressed)==payload
 r.update(status='package-gzip-roundtrip-passed',build_receipt_sha256=sha(raw),package=name,package_sha256=build['packages'][name]['sha256'],binary_sha256=sha(binary),input_sha256=sha(payload),compressed_sha256=sha(compressed),input_bytes=len(payload),compressed_bytes=len(compressed),loader_map_sha256=sha(maps.encode()))
except Exception as e:r.update(status='failed',error=str(e));raise
finally:(a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
print(r['status'])
