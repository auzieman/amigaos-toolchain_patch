#!/usr/bin/env python3
"""Package standard U-Boot board payloads; never writes a block device."""
import argparse, gzip, hashlib, json, os, shutil, struct, subprocess, zlib
from pathlib import Path
p = argparse.ArgumentParser(description=__doc__)
for n in ['kernel-results', 'shell-results', 'output']:
    p.add_argument('--'+n, type=Path, required=True)
a = p.parse_args()
sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
k = json.loads((a.kernel_results/'linux-receipt.json').read_text())
s = json.loads((a.shell_results/'receipt.json').read_text())
if k['status'] != 'compiled' or k.get('kernel_profile', 'tabor') not in ['tabor','tabor-live']:
    p.error('Compiled physical-board kernel required')
if s['status'] not in ['static-shell-initramfs-built','rescue-initramfs-extended']:
    p.error('Built source-based shell required')
kernel = a.kernel_results/'vmlinux'
dtb = a.kernel_results/'tabor-a1222.dtb'
initrd = a.shell_results/'shell.cpio'
for f, expected in [(kernel, k['artifacts']['vmlinux']),
                    (dtb, k['artifacts']['arch/powerpc/boot/dts/fsl/tabor-a1222.dtb']),
                    (initrd, s['initramfs_sha256'])]:
    if sha(f) != expected:
        p.error('Artifact hash mismatch: '+str(f))
elf = kernel.read_bytes()
if elf[:6] != b'\x7fELF\x01\x02' or struct.unpack_from('>H', elf, 18)[0] != 20:
    p.error('Expected big-endian PPC32 ELF')
phoff = struct.unpack_from('>I', elf, 28)[0]
phsize, phnum = struct.unpack_from('>HH', elf, 42)
segments = [struct.unpack_from('>8I', elf, phoff+i*phsize) for i in range(phnum)]
loads = [x for x in segments if x[0] == 1]
if not loads or min(x[3] for x in loads) != 0:
    p.error('Unexpected physical load base; review firmware map')
memory_end = max(x[3]+x[5] for x in loads)
if memory_end >= 0x04000000:
    p.error('Kernel memory extent overlaps proposed compressed-image staging')
a.output.mkdir(parents=True, exist_ok=False)
env = {**os.environ, 'SOURCE_DATE_EPOCH': '0'}
with (a.output/'packaging.log').open('w') as log:
    raw = a.output/'kernel.bin'
    subprocess.run(['powerpc-linux-gnu-objcopy', '-O', 'binary', str(kernel), str(raw)], check=True)
    for source, packed, kind in [(raw, 'uImage', 'kernel'), (initrd, 'uRamdisk', 'ramdisk')]:
        compressed = a.output/(packed+'.gz')
        compressed.write_bytes(gzip.compress(source.read_bytes(), compresslevel=9, mtime=0))
        subprocess.run(['mkimage', '-A', 'ppc', '-O', 'linux', '-T', kind,
                        '-C', 'gzip', '-a', '0', '-e', '0', '-n', 'A1222 SPE rescue',
                        '-d', str(compressed), str(a.output/packed)],
                       env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
        image = (a.output/packed).read_bytes()
        magic, hcrc, stamp, size, load, entry, dcrc = struct.unpack_from('>7I', image)
        header = bytearray(image[:64]);header[4:8] = b'\0'*4
        if (magic != 0x27051956 or len(image) != 64+size
            or zlib.crc32(header) != hcrc or zlib.crc32(image[64:]) != dcrc):
            raise RuntimeError('U-Boot header/data CRC verification failed')
        if gzip.decompress(image[64:]) != source.read_bytes():
            raise RuntimeError('Compressed payload mismatch')
        compressed.unlink()
    raw.unlink()
shutil.copy2(dtb, a.output/'tabor.dtb')
receipt = {'status': 'packaged-for-review-not-physical-boot-tested',
           'physical_boot': False, 'image_format': 'standard legacy U-Boot, PPC Linux gzip',
           'kernel_physical_memory_end': hex(memory_end),
           'proposed_ram_staging': {'uImage': '0x04000000', 'dtb': '0x08000000', 'uRamdisk': '0x0a000000'},
           'kernel_sha256': sha(kernel), 'initramfs_sha256': sha(initrd),
           'files_sha256': {n: sha(a.output/n) for n in ['uImage', 'uRamdisk', 'tabor.dtb']},
           'remaining': ['Verify selected display and USB keyboard driver in first-boot payload',
                         'Validate real firmware iminfo/load map before bootm',
                         'Reidentify SanDisk device immediately before an authorized write'],
           'usb_written': False}
(a.output/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps(receipt, indent=2))
