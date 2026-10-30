#!/usr/bin/env python3
"""Build the locked PPC emulator in a fresh local directory; no system install."""
import argparse, hashlib, json, subprocess, tarfile
from pathlib import Path
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--archive', type=Path, required=True)
p.add_argument('--work', type=Path, required=True)
a = p.parse_args()
project = Path(__file__).resolve().parent.parent
lock = json.loads((project/'profiles/qemu/amigaos-ati.json').read_text())['qemu']
if hashlib.file_digest(a.archive.open('rb'), 'sha256').hexdigest() != lock['sha256']:
    p.error('QEMU archive hash mismatch')
if a.work.exists():
    p.error('Fresh work directory required')
a.work.mkdir(parents=True)
receipt = {'source': lock, 'status': 'started', 'commands': []}
try:
    with tarfile.open(a.archive) as t:
        t.extractall(a.work, filter='data')
    source = a.work.resolve()/('qemu-'+lock['version'])
    build = a.work.resolve()/'build'
    build.mkdir()
    commands = [[str(source/'configure'), '--target-list=ppc-softmmu',
                 '--enable-vnc', '--disable-docs', '--disable-gtk',
                 '--disable-sdl', '--disable-werror', '--disable-download'],
                ['ninja', '-j2', 'qemu-system-ppc']]
    with (a.work/'build.log').open('w') as log:
        for command in commands:
            receipt['commands'].append(command)
            subprocess.run(command, cwd=build, stdout=log,
                           stderr=subprocess.STDOUT, check=True)
    binary = build/'qemu-system-ppc'
    receipt.update(status='compiled', binary_sha256=hashlib.file_digest(
        binary.open('rb'), 'sha256').hexdigest(), version=subprocess.check_output(
            [str(binary), '--version'], text=True).splitlines()[0])
except Exception as e:
    receipt.update(status='failed', error=str(e))
    raise
finally:
    (a.work/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
