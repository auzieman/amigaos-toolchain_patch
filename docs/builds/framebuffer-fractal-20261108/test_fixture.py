"""R730-only: run the exact PPC presenter against a RAM-like file, no GPU."""
from pathlib import Path
import hashlib
import json
import re
import struct
import subprocess

w = Path('/home/owner/fb-fractal-20261108')
fb = w / 'fixture.fb'
backup = w / 'fixture.backup'
assert not fb.exists() and not backup.exists()
original = b'\x5a' * (1920 * 1080 * 4)
fb.write_bytes(original)
counts = (w / 'counts.bin').read_bytes()
assert len(counts) == 128 * 96


def run(*args, expected=0):
    p = subprocess.run(['qemu-ppc', '-cpu', 'e500v2', str(w / 'fb-fractal'), *map(str, args)],
                       capture_output=True, text=True, timeout=15)
    assert p.returncode == expected, (args, p.returncode, p.stdout, p.stderr)
    return p.stdout


draw = run('--fixture', w / 'counts.bin', backup, fb)
expected = bytearray(original)
for y in range(96):
    row = bytearray()
    for n in counts[y * 128:(y + 1) * 128]:
        pixel = 0 if n == 96 else ((n * 13 % 256) << 16) | ((n * 7 % 256) << 8) | (n * 19 % 256)
        row.extend(struct.pack('>I', pixel) * 8)
    for dy in range(8):
        offset = ((156 + y * 8 + dy) * 1920 + 448) * 4
        expected[offset:offset + len(row)] = row
assert fb.read_bytes() == expected, 'PPC draw differs from independent native-BE pixel/offset model'
restore = run('--fixture-restore', backup, fb)
assert fb.read_bytes() == original, 'restore failed'
bad = w / 'bad-counts.bin'
bad.write_bytes(b'\x61' + counts[1:])
negative = run('--fixture', bad, w / 'must-not-create.backup', fb, expected=1)
assert not (w / 'must-not-create.backup').exists() and fb.read_bytes() == original
disassembly = (w / 'disassembly.txt').read_text()
assert not re.search(r'\s(?:efs\w+|efd\w+|fadd\w*|fsub\w*|fmul\w*|fdiv\w*|lfd|lfs|stfd|stfs)\s', disassembly)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
receipt = {'status': 'PASS', 'device_access': False, 'cpu': 'QEMU e500v2',
           'source_sha256': sha(w / 'fb-fractal.c'), 'binary_sha256': sha(w / 'fb-fractal'),
           'counts_sha256': sha(w / 'counts.bin'), 'draw_output': draw,
           'restore_output': restore, 'negative_output': negative,
           'exact_whole_file_draw_comparison': True, 'exact_restore': True,
           'invalid_input_refused_before_backup_or_drawing': True,
           'no_float_instructions_in_integer_only_presenter': True,
           'physical_scanout_accepted': False}
(w / 'fixture-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
