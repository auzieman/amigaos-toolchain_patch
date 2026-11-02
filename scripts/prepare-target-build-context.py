#!/usr/bin/env python3
"""Prepare real target library packages for a normal Debian cross-build root.

No payload extraction, version rewriting, dependency substitution or package
installation happens here. apt/dpkg perform installation in the Docker recipe.
"""
import argparse, hashlib, json, shutil, subprocess
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
for name in ['base', 'manifest', 'dockerfile', 'output']:
    p.add_argument('--' + name, type=Path, required=True)
a = p.parse_args()
sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
spec = json.loads(a.manifest.read_text())
a.output.mkdir(exist_ok=False)
dest = a.output / 'packages'; dest.mkdir()
inputs = []; checksums = []
for item in spec['inputs']:
    receipt = (a.base / item['receipt']).resolve()
    assert receipt.is_relative_to(a.base.resolve())
    assert sha(receipt) == item['receipt_sha256']
    original = json.loads(receipt.read_text())
    assert original['status'] == 'debian-packages-built-not-target-installed'
    found = set()
    for name, entry in original['packages'].items():
        assert Path(name).name == name
        if not name.endswith('.deb'):
            continue
        path = receipt.parent / name
        assert sha(path) == entry['sha256']
        package, arch = subprocess.check_output(
            ['dpkg-deb', '-f', str(path), 'Package', 'Architecture'], text=True).splitlines()
        package = package.removeprefix('Package: ')
        arch = arch.removeprefix('Architecture: ')
        if package not in item['packages']:
            continue
        assert arch == 'powerpcspe' or (arch == 'all' and item.get('allow_arch_all')), 'Only target libraries or explicitly reviewed independent data enter this context'
        assert not (dest / name).exists()
        shutil.copyfile(path, dest / name)
        checksums.append(entry['sha256'] + '  ' + name)
        found.add(package)
        inputs.append({'package': package, 'file': name, 'sha256': entry['sha256'],
                       'receipt_sha256': item['receipt_sha256'],
                       'build_profiles': original.get('build_profiles')})
    assert found == set(item['packages'])
assert inputs
(dest / 'SHA256SUMS').write_text('\n'.join(checksums) + '\n')
shutil.copyfile(a.dockerfile, a.output / 'Dockerfile')
(a.output / 'provenance.json').write_text(json.dumps({
    'recipe_sha256': sha(Path(__file__)), 'manifest_sha256': sha(a.manifest),
    'dockerfile_sha256': sha(a.dockerfile), 'inputs': inputs,
    'purpose': 'isolated cross-build root; not a final target installation'}, indent=2) + '\n')
