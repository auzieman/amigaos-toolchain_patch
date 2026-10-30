#!/usr/bin/env python3
"""Stage verified board artifacts for review; never writes devices or invents firmware headers."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--kernel-results', type=Path, required=True)
p.add_argument('--spe-results', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
k = json.loads((a.kernel_results / 'linux-receipt.json').read_text())
s = json.loads((a.spe_results / 'receipt.json').read_text())
if k['status'] != 'compiled' or k.get('kernel_profile', 'tabor') != 'tabor':
    p.error('compiled real-board profile required')
if not s.get('selected_spe_arithmetic_passed') or s['status'] != 'passed':
    p.error('verified SPE initramfs receipt required')
files = [(a.kernel_results / 'vmlinux', 'vmlinux', k['artifacts']['vmlinux']),
         (a.kernel_results / 'tabor-a1222.dtb', 'tabor-a1222.dtb', k['artifacts']['arch/powerpc/boot/dts/fsl/tabor-a1222.dtb']),
         (a.kernel_results / 'kernel.config', 'kernel.config', k['config_sha256']),
         (a.spe_results / 'initramfs.cpio', 'initramfs-spe.cpio', s['initramfs_sha256'])]
for source, _, expected in files:
    if sha(source) != expected:
        p.error('input hash mismatch: ' + str(source))
output = a.output.resolve()
if output.is_relative_to('/dev') or any(output.is_relative_to(x.resolve()) for x in [a.kernel_results, a.spe_results]):
    p.error('independent regular output directory required')
output.mkdir(parents=True, exist_ok=False)
manifest = {'status': 'staged-not-firmware-boot-ready', 'physical_boot_tested': False,
            'graphics_tested': False, 'rootfs_included': False, 'files': {},
            'pending': ['Verify real Tabor firmware wrapper/load addresses against reference image',
                        'Provide compatible SPE rootfs for E/Xorg/Mesa/gears',
                        'Identify A1222 AMD PCI ID and firmware requirements',
                        'Physical boot and GPU validation']}
for source, name, expected in files:
    shutil.copyfile(source, output / name)
    assert sha(output / name) == expected
    manifest['files'][name] = expected
shutil.copyfile(a.kernel_results / 'linux-receipt.json', output / 'kernel-receipt.json')
shutil.copyfile(a.spe_results / 'receipt.json', output / 'qemu-spe-receipt.json')
(output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
(output / 'README.txt').write_text('''A1222 physical test staging — not a bootable USB image yet.
Contains the full Tabor kernel/DTB and a libc-free SPE arithmetic initramfs.
The initramfs is shared with the successful QEMU arithmetic test; the kernel
is the independently compiled board profile, not the QEMU kernel.
No disk partitioning, firmware changes or media writes were performed.
Do not run the old zero-padding wrapper as a verified Tabor boot format.
Reference firmware wrapper and memory load addresses still require review.
E/Xorg/Mesa/gears and an interactive rootfs are NOT included.
Retain the machine serial log when eventually testing these artifacts.
''')
print(output)
