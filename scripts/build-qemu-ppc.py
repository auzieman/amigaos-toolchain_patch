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
    # Ordered, hash-pinned target/ppc corrections (patches/qemu/series.json).
    series = json.loads((project/'patches/qemu/series.json').read_text())
    if series['version'] != lock['version']:
        raise RuntimeError('QEMU patch series is for another version')
    plain = [l for l in (project/'patches/qemu/series').read_text().splitlines()
             if l and not l.startswith('#')]
    if plain != [Path(x['path']).name for x in series['patches']]:
        raise RuntimeError('QEMU series differs from series.json')
    receipt['patches'] = []
    for item in series['patches']:
        patch = project/item['path']
        if hashlib.sha256(patch.read_bytes()).hexdigest() != item['sha256']:
            raise RuntimeError('QEMU patch hash mismatch: ' + item['path'])
        subprocess.run(['patch', '-p1', '--batch', '--forward', '--no-backup-if-mismatch'],
                       cwd=source, input=patch.read_bytes(), check=True)
        receipt['patches'].append(item)
    dtc = source/'subprojects/dtc'
    subprocess.run(['git', 'init', str(dtc)], check=True)
    subprocess.run(['git', '-C', str(dtc), 'remote', 'add', 'origin', lock['dtc']['url']], check=True)
    subprocess.run(['git', '-C', str(dtc), 'fetch', '--depth', '1', 'origin', lock['dtc']['revision']], check=True)
    subprocess.run(['git', '-C', str(dtc), 'checkout', '--detach', 'FETCH_HEAD'], check=True)
    actual = subprocess.check_output(['git', '-C', str(dtc), 'rev-parse', 'HEAD'], text=True).strip()
    if actual != lock['dtc']['revision']:
        raise RuntimeError('DTC revision mismatch')
    receipt['dtc_revision'] = actual
    build = a.work.resolve()/'build'
    build.mkdir()
    commands = [[str(source/'configure'), '--target-list=ppc-softmmu',
                 '--enable-vnc', '--enable-fdt=internal', '--disable-docs', '--disable-gtk',
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
