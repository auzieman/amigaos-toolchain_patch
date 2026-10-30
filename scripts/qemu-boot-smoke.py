#!/usr/bin/env python3
"""Boot a PPC32 kernel into a freestanding init; retain bounded serial evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import stat
import re

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--kernel', type=Path, required=True)
p.add_argument('--init-source', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--image-id', required=True)
a = p.parse_args()
if not re.fullmatch(r'sha256:[0-9a-f]{64}', a.image_id):
    p.error('exact image identity required')
if not all(x.is_absolute() for x in [a.kernel, a.init_source, a.output]):
    p.error('absolute paths required')
a.output.mkdir(parents=True, exist_ok=False)
root = a.output / 'root'
root.mkdir()

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

receipt = {'image_id': a.image_id, 'kernel_sha256': digest(a.kernel),
           'init_source_sha256': digest(a.init_source), 'spe_validated': False,
           'glibc_validated': False, 'real_board_boot': False, 'status': 'started'}
try:
    subprocess.run(['powerpc-linux-gnu-as', '-me500', '-o', str(a.output / 'init.o'), str(a.init_source)], check=True)
    subprocess.run(['powerpc-linux-gnu-ld', '-static', '-e', '_start', '-o', str(root / 'init'), str(a.output / 'init.o')], check=True)
    (root / 'init').chmod(0o755)
    # Include /dev/console without creating host device nodes or requiring privileges.
    with (a.output / 'initramfs.cpio').open('wb') as archive:
        def entry(name, mode, data=b'', major=0, minor=0):
            encoded = name.encode() + b'\0'
            fields = [0, mode, 0, 0, 1, 0, len(data), 0, 0, major, minor, len(encoded), 0]
            header = b'070701' + ''.join(f'{v:08x}' for v in fields).encode()
            archive.write(header + encoded)
            archive.write(b'\0' * (-(len(header) + len(encoded)) % 4))
            archive.write(data + b'\0' * (-len(data) % 4))
        entry('dev', stat.S_IFDIR | 0o755)
        entry('dev/console', stat.S_IFCHR | 0o600, major=5, minor=1)
        entry('init', stat.S_IFREG | 0o755, (root / 'init').read_bytes())
        entry('TRAILER!!!', 0)
    receipt['init_sha256'] = digest(root / 'init')
    receipt['initramfs_sha256'] = digest(a.output / 'initramfs.cpio')
    receipt['qemu_version'] = subprocess.check_output(['qemu-system-ppc', '--version'], text=True)
    cmd = ['qemu-system-ppc', '-M', 'ppce500', '-cpu', 'e500v2', '-accel', 'tcg',
           '-smp', '2', '-m', '512M', '-display', 'none', '-serial', 'stdio',
           '-monitor', 'none', '-nic', 'none', '-no-reboot',
           '-kernel', str(a.kernel), '-initrd', str(a.output / 'initramfs.cpio'),
           '-append', 'console=ttyS0,115200 rdinit=/init panic=-1']
    receipt['command'] = cmd
    with (a.output / 'serial.log').open('wb', buffering=0) as serial:
        proc = subprocess.Popen(cmd, stdout=serial, stderr=subprocess.STDOUT)
        try:
            proc.wait(timeout=60)
            receipt['termination'] = 'qemu-exited'
        except subprocess.TimeoutExpired:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            receipt['termination'] = 'bounded-test-timeout'
    log = (a.output / 'serial.log').read_bytes()
    receipt['serial_sha256'] = digest(a.output / 'serial.log')
    receipt['init_reached'] = b'TABOR_QEMU_INIT_OK:' in log
    receipt['panic_seen'] = b'Kernel panic' in log
    receipt['selected_spe_arithmetic_passed'] = b'SPE_SMOKE_PASS:' in log and b'SPE_SMOKE_FAIL:' not in log
    receipt['status'] = 'passed' if receipt['init_reached'] and not receipt['panic_seen'] else 'failed'
except Exception as exc:
    receipt['status'] = 'failed'
    receipt['error'] = str(exc)
    raise
finally:
    (a.output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
raise SystemExit(0 if receipt['status'] == 'passed' else 1)
