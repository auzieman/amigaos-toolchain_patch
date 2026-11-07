#!/usr/bin/env python3
"""Bounded serial test of an existing SPE userspace with a selected kernel."""
import argparse, hashlib, json, os, re, shutil, subprocess, time
from pathlib import Path
p = argparse.ArgumentParser(description=__doc__)
for name in ('kernel', 'disk', 'output'):
    p.add_argument('--' + name, type=Path, required=True)
p.add_argument('--timeout', type=int, default=150)
p.add_argument('--cpus', type=int, choices=(1, 2), default=2)
p.add_argument('--expected-release', required=True)
p.add_argument('--kernel-arg', action='append', default=[])
a = p.parse_args()
if not 30 <= a.timeout <= 300:
    p.error('timeout must be between 30 and 300 seconds')
a.output.mkdir(parents=True, exist_ok=False)
def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()
qemu = shutil.which('qemu-system-ppc')
if not qemu:
    p.error('qemu-system-ppc not installed')
cmd = [qemu, '-M', 'ppce500', '-cpu', 'e500v2', '-accel', 'tcg',
       '-smp', str(a.cpus), '-m', '1024M', '-display', 'none', '-serial', 'stdio',
       '-monitor', 'none', '-nic', 'none', '-no-reboot', '-kernel', str(a.kernel),
       '-drive', 'file=' + str(a.disk) + ',format=raw,if=none,id=rootdisk,snapshot=on',
       '-device', 'virtio-blk-pci,drive=rootdisk', '-append',
       'console=ttyS0,115200 root=PARTUUID=a1221105-02 rootfstype=ext4 rootwait rw init=/init panic=-1']
cmd[-1] += ''.join(' ' + arg for arg in a.kernel_arg)
r = {'status': 'started', 'command': cmd, 'kernel_sha256': sha(a.kernel),
     'disk_sha256_before': sha(a.disk), 'qemu_sha256': sha(Path(qemu)),
     'qemu_version': subprocess.check_output([qemu, '--version'], text=True).splitlines()[0],
     'physical_boot': False, 'radeon_validated': False, 'full_trixie_root_validated': False,
     'modern_spe_compiler_validated': False, 'disk_snapshot': True, 'network': 'disabled'}
serial = a.output / 'serial.log'
proc = None
sent = False
def constrain():
    os.sched_setaffinity(0, sorted(os.sched_getaffinity(0))[:2])
    # Run under the server memory cgroup; QEMU virtual mappings exceed resident RAM.
try:
    with serial.open('wb', buffering=0) as log:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=log,
                                stderr=subprocess.STDOUT, preexec_fn=constrain)
        deadline = time.monotonic() + a.timeout
        while time.monotonic() < deadline:
            data = serial.read_bytes().replace(b'\r', b'')
            if b'Kernel panic' in data or proc.poll() is not None:
                break
            if b'SHELL_READY\n' in data and not sent:
                time.sleep(.5)
                command = (b"stty -echo; printf '\\nRUNTIME_BEGIN\\n'; uname -r; uname -m; "
                           b"head -n 2 /proc/meminfo; cat /etc/os-release; "
                           b"/bin/spe-abi-check --cli; printf '\\nABI_EXIT=%s\\n' $?; "
                           b"/bin/fractal-test; printf '\\nFRACTAL_EXIT=%s\\nRUNTIME_DONE\\n' $?\n")
                proc.stdin.write(command)
                proc.stdin.flush()
                sent = True
            if re.search(rb'^RUNTIME_DONE$', data, re.M):
                break
            time.sleep(.2)
except Exception as error:
    r['error'] = str(error)
finally:
    if proc is not None and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
    data = serial.read_bytes().replace(b'\r', b'') if serial.exists() else b''
    checks = {k.decode(): v.decode() for k, v in re.findall(rb'^ABI_TEST (\w+) (PASS|FAIL)$', data, re.M)}
    required = {'float32', 'float64', 'varargs', 'formatting', 'fenv', 'setjmp', 'signal', 'pthread_tls', 'ucontext'}
    r.update(commands_sent=sent, shell_ready=b'SHELL_READY\n' in data,
             runtime_done=bool(re.search(rb'^RUNTIME_DONE$', data, re.M)),
             panic_seen=b'Kernel panic' in data, abi_checks=checks,
             abi_all_passed=set(checks) == required and all(v == 'PASS' for v in checks.values()),
             abi_exit=re.findall(rb'^ABI_EXIT=(\d+)$', data, re.M)[-1:].pop().decode() if re.search(rb'^ABI_EXIT=(\d+)$', data, re.M) else None)
    trials = re.findall(rb'FRACTAL_TIME mode=(SOFT|SPE) trial=(\d+) us=(\d+) checksum=(\d+)', data)
    r['fractal_trials'] = [{'mode': m.decode(), 'trial': int(t), 'us': int(u), 'checksum': int(c)} for m,t,u,c in trials]
    images = {m: bytes.fromhex(v.decode()) for m,v in re.findall(rb'FRACTAL_PIXELS mode=(SOFT|SPE) ([0-9a-f]+)', data)}
    pixel_hash = 2166136261
    for pixel in images.get(b'SOFT', b''):
        pixel_hash = ((pixel_hash ^ pixel) * 16777619) & 0xffffffff
    r['fractal_equal'] = (len(trials) == 6 and all(int(c) == 0xabd5de74 for _,_,_,c in trials)
                          and all(int(u) > 0 for _,_,u,_ in trials)
                          and sorted((m,int(t)) for m,t,_,_ in trials) == [(m,t) for m in [b'SOFT',b'SPE'] for t in [1,2,3]]
                          and pixel_hash == 0xabd5de74
                          and len(images.get(b'SOFT', b'')) == 12288
                          and images.get(b'SOFT') == images.get(b'SPE')
                          and bool(re.search(rb'^FRACTAL_EXIT=0$', data, re.M)))
    r['release_reported'] = bool(re.search(rb'^' + re.escape(a.expected_release.encode()) + rb'$', data, re.M))
    r['machine_reported_ppc'] = bool(re.search(rb'^ppc$', data, re.M))
    r['kernel_boot_passed'] = (r['shell_ready'] and sent and r['runtime_done'] and not r['panic_seen']
                               and r['release_reported'] and r['machine_reported_ppc'])
    r['disk_sha256_after'] = sha(a.disk)
    r['disk_unchanged'] = r['disk_sha256_before'] == r['disk_sha256_after']
    r['status'] = ('passed-selected-runtime-checks' if r['kernel_boot_passed'] and r['abi_all_passed']
                   and r['abi_exit'] == '0' and r['fractal_equal'] and r['disk_unchanged']
                   else 'incomplete-or-runtime-failure')
    if serial.exists(): r['serial_sha256'] = sha(serial)
    (a.output / 'receipt.json').write_text(json.dumps(r, indent=2) + '\n')
print(json.dumps({k:v for k,v in r.items() if k != 'command'}, indent=2))
raise SystemExit(0 if r['status'] == 'passed-selected-runtime-checks' else 1)
