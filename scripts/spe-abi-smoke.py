#!/usr/bin/env python3
"""Compile and run a bounded C ABI check with the restored SPE sysroot."""
import argparse, hashlib, json, re, subprocess, sys
from pathlib import Path
p = argparse.ArgumentParser(description=__doc__)
for name in ['project', 'tools', 'sysroot', 'kernel', 'output']:
    p.add_argument('--'+name, type=Path, required=True)
p.add_argument('--image-id', required=True)
a = p.parse_args()
a.output.mkdir(parents=True, exist_ok=False)
source = a.project/'bench/spe-abi-smoke.c'
binary = a.output/'abi-init'
cc = a.tools/'bin/powerpc-linux-gnuspe-gcc'
flags = ['--sysroot='+str(a.sysroot), '-isystem', str(a.sysroot/'usr/include'),
         '-B'+str(a.sysroot/'usr/lib')+'/', '-mcpu=8548', '-mabi=spe',
         '-mspe', '-mfloat-gprs=double', '-mlong-double-128', '-O2', '-g0', '-frounding-math',
         '-static', '-pthread']
digest = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
receipt = {'status': 'started', 'image_id': a.image_id,
           'source_sha256': digest(source), 'full_spe_abi_validated': False,
           'physical_boot': False, 'flags': flags}
try:
    with (a.output/'build.log').open('w') as log:
        subprocess.run([str(cc)]+flags+[str(source), '-lm', '-o', str(binary)],
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    disassembly = subprocess.check_output(['powerpc-linux-gnu-objdump', '-d', str(binary)])
    (a.output/'disassembly.txt').write_bytes(disassembly)
    receipt['binary_sha256'] = digest(binary)
    receipt['spe_single_arithmetic_present'] = bool(re.search(rb'\befsadd\b', disassembly))
    receipt['spe_double_arithmetic_present'] = bool(re.search(rb'\befdadd\b', disassembly))
    subprocess.run([sys.executable, str(a.project/'scripts/qemu-boot-smoke.py'),
                    '--kernel', str(a.kernel), '--init-binary', str(binary),
                    '--output', str(a.output/'boot'), '--timeout', '20',
                    '--image-id', a.image_id], check=True)
    boot = json.loads((a.output/'boot/receipt.json').read_text())
    serial = (a.output/'boot/serial.log').read_bytes().replace(b'\r', b'')
    names = ['float32', 'float64', 'varargs', 'formatting', 'fenv', 'setjmp',
             'signal', 'pthread_tls', 'ucontext']
    receipt['checks'] = {n: bool(re.search(
        rb'^ABI_TEST '+n.encode()+rb' PASS$', serial, re.M)) for n in names}
    receipt['check_status'] = {n: (re.search(rb'^ABI_TEST '+n.encode()+rb' ([A-Z_]+)$', serial, re.M).group(1).decode() if re.search(rb'^ABI_TEST '+n.encode()+rb' ([A-Z_]+)$', serial, re.M) else 'NOT_REACHED') for n in names}
    receipt['fenv_check_status'] = {name.decode(): status.decode() for name, status in re.findall(rb'^FENV_CHECK (\w+) (PASS|FAIL)$', serial, re.M)}
    receipt['kernel_futex_missing'] = b'ABI_TEST pthread_tls SKIP_KERNEL_FUTEX' in serial
    receipt['long_double_bits'] = 128
    receipt['serial_sha256'] = boot['serial_sha256']
    receipt['status'] = 'passed-basic-C-checks' if (
        boot['status'] == 'passed' and all(receipt['checks'].values())
        and re.search(rb'^ABI_SMOKE_DONE failures=0$', serial, re.M)
        and receipt['spe_single_arithmetic_present']
        and receipt['spe_double_arithmetic_present']) else 'failed'
except Exception as e:
    receipt.update(status='failed', error=str(e))
    raise
finally:
    (a.output/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps(receipt, indent=2))
raise SystemExit(0 if receipt['status'] == 'passed-basic-C-checks' else 1)
