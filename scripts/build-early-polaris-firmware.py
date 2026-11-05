#!/usr/bin/env python3
"""Package pinned firmware only for early AMDGPU probing, retaining ext4 root."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import stat
import struct
import subprocess
import zlib

p=argparse.ArgumentParser(description=__doc__)
for name in ['firmware-deb','firmware-lock','boot-command','output']:
    p.add_argument('--'+name,type=Path,required=True)
a=p.parse_args()
sha=lambda data:hashlib.sha256(data).hexdigest()
lock=json.loads(a.firmware_lock.read_text())
assert sha(a.firmware_deb.read_bytes())==lock['sha256']
a.output.mkdir(parents=True,exist_ok=False)
extracted=a.output/'package'
subprocess.run(['dpkg-deb','-x',str(a.firmware_deb),str(extracted)],check=True)
firmware=extracted/'usr/lib/firmware/amdgpu'
files={}
for path in sorted(firmware.glob('polaris1[01]*')):
    # Materialize package symlinks so every archive entry is self-contained.
    assert path.resolve().is_relative_to(firmware.resolve())
    files['lib/firmware/amdgpu/'+path.name]=path.read_bytes()
assert 'lib/firmware/amdgpu/polaris11_sdma.bin' in files
files['usr/share/licenses/firmware-amd-graphics/copyright']=(extracted/'usr/share/doc/firmware-amd-graphics/copyright').read_bytes()
archive=bytearray()
def entry(name,mode,data=b''):
    raw=name.encode()+b'\0'
    fields=[0,mode,0,0,1,0,len(data),0,0,0,0,len(raw),0]
    header=b'070701'+''.join(f'{value:08x}' for value in fields).encode()
    archive.extend(header+raw+b'\0'*(-(len(header)+len(raw))%4))
    archive.extend(data+b'\0'*(-len(data)%4))
dirs=set()
for name in files:
    dirs.update(str(parent) for parent in Path(name).parents if str(parent)!='.')
for name in sorted(dirs,key=lambda x:(x.count('/'),x)):
    entry(name,stat.S_IFDIR|0o755)
for name,data in sorted(files.items()):
    entry(name,stat.S_IFREG|0o644,data)
entry('TRAILER!!!',0)
# There is deliberately no /init: kernel mounts root=PARTUUID normally.
assert 'init' not in files
cpio=a.output/'firmware.cpio';cpio.write_bytes(archive)
packed=a.output/'firmware.cpio.gz';packed.write_bytes(gzip.compress(archive,mtime=0))
ramdisk=a.output/'uRamdisk-fw'
subprocess.run(['mkimage','-A','ppc','-O','linux','-T','ramdisk','-C','gzip',
                '-a','0','-e','0','-n','Polaris early firmware','-d',str(packed),str(ramdisk)],check=True)
raw=ramdisk.read_bytes();header=bytearray(raw[:64]);expected=struct.unpack_from('>I',header,4)[0];header[4:8]=b'\0'*4
assert zlib.crc32(header)&0xffffffff==expected
assert zlib.crc32(raw[64:])&0xffffffff==struct.unpack_from('>I',raw,24)[0]
assert gzip.decompress(raw[64:])==archive
command=a.boot_command.read_text()
line='    bootm 0x04000000 - 0x08000000'
assert command.count(line)==1
command=command.replace(line,'''    if fatload usb 0:1 0x0a000000 /boot/uRamdisk-fw; then
     if iminfo 0x0a000000; then
      bootm 0x04000000 0x0a000000 0x08000000
     fi
    fi''')
(a.output/'boot.cmd').write_text(command)
subprocess.run(['mkimage','-A','ppc','-O','linux','-T','script','-C','none',
                '-n','A1222 early Polaris firmware','-d',str(a.output/'boot.cmd'),str(a.output/'boot.scr')],check=True)
receipt={'status':'early-firmware-archive-built','firmware_package':lock,
         'files_sha256':{n:sha(d) for n,d in files.items()},'firmware_files':len(files)-1,
         'archive_has_init':False,'root_filesystem':'unchanged ext4 PARTUUID',
         'artifacts':{n:sha((a.output/n).read_bytes()) for n in ['firmware.cpio','uRamdisk-fw','boot.cmd','boot.scr']},
         'uRamdisk_bytes':ramdisk.stat().st_size,'physical_display_verified':False}
(a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='files_sha256'},indent=2))
