#!/usr/bin/env python3
"""Render captured correctness evidence without inventing benchmark timings."""
import hashlib
import json
from pathlib import Path

project = Path(__file__).resolve().parents[1]
base = project / 'docs/builds'
boot = json.loads((base / '20261030-qemu-boot.json').read_text())['boot']
spe = json.loads((base / '20261030-qemu-spe-arithmetic.json').read_text())
if boot['kernel_sha256'] != spe['kernel_sha256']:
    raise SystemExit('Comparison requires the same kernel')
for receipt, filename in [(boot, '20261030-qemu-serial.log'), (spe, '20261030-qemu-spe-serial.log')]:
    if hashlib.sha256((base / filename).read_bytes()).hexdigest() != receipt['serial_sha256']:
        raise SystemExit('Serial evidence hash mismatch: ' + filename)
def passed(value):
    return 'PASS' if value else 'NOT PASSED'
rows = [
    ('Kernel enters userspace', passed(boot['init_reached']), passed(spe['init_reached'])),
    ('Single: 1.5 + 2.25 = 3.75', 'NOT RUN', passed(spe['selected_spe_arithmetic_passed'])),
    ('Double: 1.5 + 2.25 = 3.75', 'NOT RUN', passed(spe['selected_spe_arithmetic_passed'])),
    ('SPE register load/store', 'NOT RUN', passed(spe['selected_spe_arithmetic_passed'])),
    ('Kernel panic observed', str(boot['panic_seen']).upper(), str(spe['panic_seen']).upper()),
    ('Matched arithmetic timing', 'NOT MEASURED', 'NOT MEASURED'),
    ('Throughput / speedup', 'N/A', 'N/A'),
]
line = '+' + '-' * 32 + '+' + '-' * 18 + '+' + '-' * 18 + '+'
print('A1222 / e500v2 - CAPTURED TEST RESULTS - 2026-10-30')
print('Linux 6.12.113 | QEMU 10.0.13 TCG | 2 CPUs | 512 MiB')
print(line)
print(f'| {"Check":<30} | {"No-SPE init":<16} | {"SPE test init":<16} |')
print(line)
for label, left, right in rows:
    print(f'| {label:<30} | {left:<16} | {right:<16} |')
print(line)
print('Both runs use the same SPE-capable CPU model and kernel.')
print('No-SPE init = syscall-only boot baseline; no arithmetic workload.')
print('SPE PASS = selected instructions, not full ABI/glibc validation.')
print('These boot/arithmetic runs contain no matched performance timing.')
print('The 60-second harness limit is NOT an arithmetic timing result.')
print('Matched fractal timings: docs/builds/fractal-20261030/results-ascii.txt')
print('QEMU timings would describe emulation, not real A1222 performance.')
