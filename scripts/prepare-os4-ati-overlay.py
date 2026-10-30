#!/usr/bin/env python3
"""Create a private BBoot Kickstart overlay; preserve original media/files."""
import argparse, hashlib, json, zipfile
from pathlib import Path
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--kickstart', type=Path, required=True,
               help='Prepared machine-matched Kickstart directory, with official updates')
p.add_argument('--driver', type=Path, required=True)
p.add_argument('--machine', choices=['amigaone', 'pegasos2'], required=True)
p.add_argument('--output', type=Path, required=True,
               help='Private ignored output directory; no redistribution')
a = p.parse_args()
project = Path(__file__).resolve().parent.parent
lock = json.loads((project/'profiles/qemu/amigaos-ati.json').read_text())
if hashlib.file_digest(a.driver.open('rb'), 'sha256').hexdigest() != lock['driver']['sha256']:
    p.error('Driver archive hash mismatch')
layout = (a.kickstart/'Kicklayout').read_text(errors='replace')
if 'a1222' in layout.lower() or 'tabor' in layout.lower():
    p.error('A1222 Kickstart is not a matching kernel for these QEMU boards')
if not (a.kickstart/'kernel').is_file() or not (a.kickstart/'ATIRadeon.chip').is_file():
    p.error('Expected kernel and ATIRadeon.chip in prepared Kickstart')
if not any(a.output.resolve().is_relative_to(project/name) for name in ['work', 'private']):
    p.error('Output must remain under ignored project work/ or private/')
if a.output.exists():
    p.error('Fresh private output directory required')
files = sorted(a.kickstart.rglob('*'))
if any(f.is_symlink() for f in files):
    p.error('Symlinks not accepted in Kickstart overlay')
if not any('ATIRadeon.chip' in l and l.lstrip().startswith('MODULE')
           for l in layout.splitlines()):
    p.error('Kicklayout must enable ATIRadeon.chip')
a.output.mkdir(parents=True)
with zipfile.ZipFile(a.driver) as driver:
    replacement = driver.read('ATIRadeon.chip')
hashes = {}
with zipfile.ZipFile(a.output/'Kickstart.zip', 'x', zipfile.ZIP_DEFLATED) as z:
    for f in files:
        if not f.is_file():
            continue
        rel = f.relative_to(a.kickstart)
        data = replacement if str(rel) == 'ATIRadeon.chip' else f.read_bytes()
        hashes[str(rel)] = hashlib.sha256(data).hexdigest()
        z.writestr('Kickstart/'+rel.as_posix(), data)
(a.output/'receipt.json').write_text(json.dumps({
    'machine': a.machine, 'status': 'private-overlay-prepared-not-boot-tested',
    'machine_kernel_match': 'operator-supplied; not inferred from filenames',
    'driver': lock['driver'], 'files_sha256': hashes,
    'graphics_args': lock['graphics_args'],
    'redistribution_permitted': False}, indent=2)+'\n')
print('Prepared private overlay; original Kickstart files unchanged')
