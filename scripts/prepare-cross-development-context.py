#!/usr/bin/env python3
"""Prepare a hash-checked Docker context from genuine dpkg-cross output."""
import argparse, hashlib, json, shutil, subprocess
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--receipt', type=Path, required=True)
p.add_argument('--dockerfile', type=Path, required=True)
p.add_argument('--host-toolchain-receipt', type=Path,
               help='Include the recorded native compiler SDK package')
p.add_argument('--output', type=Path, required=True)
p.add_argument('packages', nargs='+', help='Exact converted binary package names')
a = p.parse_args()
sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
r = json.loads(a.receipt.read_text())
assert r['status'] == 'cross-development-packages-built-not-installed'
a.output.mkdir(exist_ok=False)
dest = a.output / 'packages'; dest.mkdir()
found = set(); checksums = []
for name, entry in r['packages'].items():
    assert Path(name).name == name
    path = a.receipt.parent / name
    assert sha(path) == entry['sha256']
    package = subprocess.check_output(['dpkg-deb', '-f', str(path), 'Package'], text=True).strip()
    if package not in a.packages:
        continue
    assert package.endswith('-powerpcspe-cross')
    shutil.copyfile(path, dest / name)
    checksums.append(entry['sha256'] + '  ' + name)
    found.add(package)
assert found == set(a.packages)
host_receipt_sha = None
if a.host_toolchain_receipt:
    host = json.loads(a.host_toolchain_receipt.read_text())
    assert host['status'] == 'native-toolchain-package-built-not-installed'
    candidates = list(a.host_toolchain_receipt.parent.glob('tabor-spe-toolchain_*_amd64.deb'))
    assert len(candidates) == 1
    path = candidates[0]
    assert sha(path) == host['package_sha256']
    assert subprocess.check_output(['dpkg-deb', '-f', str(path), 'Package'], text=True).strip() == 'tabor-spe-toolchain'
    shutil.copyfile(path, dest / path.name)
    checksums.append(host['package_sha256'] + '  ' + path.name)
    host_receipt_sha = sha(a.host_toolchain_receipt)
(dest / 'SHA256SUMS').write_text('\n'.join(checksums) + '\n')
shutil.copyfile(a.dockerfile, a.output / 'Dockerfile')
(a.output / 'provenance.json').write_text(json.dumps({
    'receipt_sha256': sha(a.receipt), 'recipe_sha256': sha(Path(__file__)),
    'host_toolchain_receipt_sha256': host_receipt_sha,
    'dockerfile_sha256': sha(a.dockerfile), 'packages': sorted(found),
    'target_installation': False}, indent=2) + '\n')
