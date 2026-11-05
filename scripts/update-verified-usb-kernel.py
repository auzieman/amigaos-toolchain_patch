#!/usr/bin/env python3
"""Replace only /boot/uImage on an identified lab USB, preserving a host backup."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile

p = argparse.ArgumentParser(description=__doc__)
for name in ['device', 'boot-results', 'output']:
    p.add_argument('--'+name, type=Path, required=True)
p.add_argument('--expected-serial', required=True)
p.add_argument('--old-kernel-sha256', required=True)
a = p.parse_args()
assert os.geteuid() == 0
device = a.device.resolve()
assert stat.S_ISBLK(device.stat().st_mode)
assert not a.output.exists()
meta = json.loads((a.boot_results/'receipt.json').read_text())
match = json.loads((a.boot_results/'machine-match.json').read_text())
assert match['status'] == 'passed'


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def identity():
    fields = dict(line.split('=', 1) for line in subprocess.check_output(
        ['udevadm', 'info', '--query=property', '--name', str(device)], text=True).splitlines() if '=' in line)
    assert fields.get('ID_BUS') == 'usb' and fields.get('ID_SERIAL') == a.expected_serial
    tree = json.loads(subprocess.check_output(['lsblk', '--json', '--tree', '-o', 'NAME,PATH,TYPE,MOUNTPOINTS', str(device)], text=True))['blockdevices'][0]
    assert tree['type'] == 'disk'
    assert len(tree.get('children', [])) == 2
    for item in [tree, *tree['children']]:
        assert not any(item.get('mountpoints') or []), 'Unmount USB partitions first'
    return fields['ID_SERIAL'], tree['children'][0]['path']


expected = meta['files_sha256']['uImage']
assert sha(a.boot_results/'uImage') == expected
serial, bootdev = identity()
a.output.mkdir(parents=True)
receipt = {'status': 'started', 'serial': serial, 'physical_boot': False,
           'root_partition_written': False, 'old_kernel_sha256': a.old_kernel_sha256,
           'new_kernel_sha256': expected}
with tempfile.TemporaryDirectory(prefix='a1222-kernel-update-') as temp:
    mounted = False
    try:
        assert identity() == (serial, bootdev)
        subprocess.run(['mount', '-t', 'vfat', '-o', 'rw,nosuid,nodev,noexec', bootdev, temp], check=True)
        mounted = True
        root = Path(temp)
        kernel = root/'boot/uImage'
        assert sha(kernel) == a.old_kernel_sha256
        unchanged = {name: sha(root/name) for name in ['boot/tabor.dtb', 'boot.scr', 'boot.cmd', 'BOOT-README.txt']}
        assert unchanged['boot/tabor.dtb'] == meta['files_sha256']['tabor.dtb'], 'DTB differs; review before updating'
        backup = a.output/'previous-uImage'
        shutil.copyfile(kernel, backup)
        assert sha(backup) == a.old_kernel_sha256
        staged = root/'boot/uImage.next'
        assert not staged.exists()
        shutil.copyfile(a.boot_results/'uImage', staged)
        with staged.open('rb') as f:
            os.fsync(f.fileno())
        assert sha(staged) == expected
        os.replace(staged, kernel)
        os.sync()
        assert sha(kernel) == expected
        assert unchanged == {name: sha(root/name) for name in unchanged}
        receipt.update(status='kernel-replaced-and-readback-verified', unchanged_files_sha256=unchanged)
    except Exception as error:
        receipt['error'] = str(error)
        raise
    finally:
        if mounted:
            subprocess.run(['umount', temp], check=True)
        (a.output/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps(receipt, indent=2))
