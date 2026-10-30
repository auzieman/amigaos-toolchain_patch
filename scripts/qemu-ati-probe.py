#!/usr/bin/env python3
"""Bounded read-only Sam460/ATI device probe; does not claim an OS/driver pass."""
import argparse, hashlib, json, signal, socket, subprocess, time
from pathlib import Path
p = argparse.ArgumentParser(description=__doc__)
for name in ['qemu', 'firmware', 'iso', 'output']:
    p.add_argument('--'+name, type=Path, required=True)
p.add_argument('--seconds', type=int, default=90)
p.add_argument('--vnc-display', type=int, default=8)
a = p.parse_args()
if not 1 <= a.seconds <= 300 or not 1 <= a.vnc_display <= 99:
    p.error('Bounded duration and VNC display required')
if a.output.exists():
    p.error('Fresh output directory required')
for f in [a.qemu, a.iso]:
    if not f.is_file():
        p.error('Missing input: '+str(f))
a.output.mkdir(parents=True)
out = a.output.resolve()
version = subprocess.check_output([str(a.qemu.resolve()), '--version'], text=True)
args = [str(a.qemu.resolve()), '-L', str(a.firmware.resolve()),
        '-machine', 'sam460ex', '-accel', 'tcg', '-m', '512',
        '-rtc', 'base=localtime', '-display', 'none', '-vga', 'none',
        '-device', 'ati-vga,model=rv100,guest_hwcursor=on',
        '-vnc', '127.0.0.1:'+str(a.vnc_display), '-nic', 'none',
        '-serial', 'file:'+str(out/'serial.log'), '-monitor', 'none',
        '-qmp', 'unix:'+str(out/'qmp.sock')+',server=on,wait=off',
        '-drive', 'if=none,id=cd,format=raw,readonly=on,file='+str(a.iso.resolve()),
        '-device', 'ide-cd,drive=cd,bus=ide.1']
receipt = {'status': 'started', 'version': version.splitlines()[0],
           'command': args, 'seconds': a.seconds, 'os_boot_verified': False,
           'new_guest_driver_loaded': False, 'a1222_emulation': False,
           'note': 'ATI device/firmware probe using original A1222 CD; '
                   'matching kernel and private replacement driver remain required',
           'qemu_sha256': hashlib.file_digest(a.qemu.open('rb'), 'sha256').hexdigest(),
           'iso_sha256': hashlib.file_digest(a.iso.open('rb'), 'sha256').hexdigest()}
with (out/'qemu.log').open('w') as log:
    proc = subprocess.Popen(args, stdout=log, stderr=subprocess.STDOUT,
                            start_new_session=True)
    try:
        end = time.monotonic()+a.seconds
        while time.monotonic() < end:
            if proc.poll() is not None:
                raise RuntimeError('QEMU exited early: '+str(proc.returncode))
            time.sleep(1)
        with socket.socket(socket.AF_UNIX) as s:
            s.settimeout(10)
            s.connect(str(out/'qmp.sock'))
            f = s.makefile('rwb', buffering=0)
            f.readline()
            for command in [{'execute': 'qmp_capabilities'},
                            {'execute': 'query-status'},
                            {'execute': 'screendump', 'arguments': {
                                'filename': str(out/'display.ppm')}}]:
                f.write((json.dumps(command)+'\n').encode())
                while True:
                    result = json.loads(f.readline())
                    if 'error' in result:
                        raise RuntimeError(str(result))
                    if 'return' in result:
                        receipt[command['execute']] = result['return']
                        break
        receipt.update(status='device-probe-completed', display_sha256=
                       hashlib.file_digest((out/'display.ppm').open('rb'), 'sha256').hexdigest())
    except Exception as e:
        receipt.update(status='failed', error=str(e))
        raise
    finally:
        if proc.poll() is None:
            proc.send_signal(signal.SIGTERM)
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
        (out/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
