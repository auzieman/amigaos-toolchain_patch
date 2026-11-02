#!/usr/bin/env python3
"""Convert receipt-pinned SPE libraries with Debian dpkg-cross, for bootstrap only.

These are host cross-development packages, never final target replacements.
No package installation or target maintainer scripts run in this step.
"""
import argparse, hashlib, json, subprocess
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
for name in ['base', 'manifest', 'output']:
    p.add_argument('--' + name, type=Path, required=True)
p.add_argument('--image-id', required=True)
a = p.parse_args()
a.output.mkdir(exist_ok=False)
sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
spec = json.loads(a.manifest.read_text())
r = {'status': 'started', 'image_id': a.image_id, 'recipe_sha256': sha(Path(__file__)),
     'manifest_sha256': sha(a.manifest), 'inputs': [], 'packages': {},
     'target_installation': False, 'purpose': 'host cross-development bootstrap only'}
try:
    with (a.output / 'build.log').open('w') as log:
        for item in spec['inputs']:
            receipt = (a.base / item['receipt']).resolve()
            assert receipt.is_relative_to(a.base.resolve())
            assert sha(receipt) == item['receipt_sha256']
            original = json.loads(receipt.read_text())
            assert original['status'] == 'debian-packages-built-not-target-installed'
            found = set()
            for name, entry in original['packages'].items():
                if not name.endswith('.deb'):
                    continue
                assert Path(name).name == name
                path = receipt.parent / name
                assert sha(path) == entry['sha256']
                package = subprocess.check_output(['dpkg-deb', '-f', str(path), 'Package'], text=True).strip()
                if package not in item['packages']:
                    continue
                arch = subprocess.check_output(['dpkg-deb', '-f', str(path), 'Architecture'], text=True).strip()
                assert arch == 'powerpcspe'
                command = ['dpkg-cross', '-a', 'powerpcspe', '-M', '-b', str(path)]
                log.write(repr(command) + '\n'); log.flush()
                subprocess.run(command, cwd=a.output, stdout=log, stderr=subprocess.STDOUT, check=True)
                found.add(package)
                r['inputs'].append({'package': package, 'sha256': sha(path), 'receipt_sha256': sha(receipt)})
            assert found == set(item['packages']), (found, item['packages'])
        for package in sorted(a.output.glob('*.deb')):
            metadata = subprocess.check_output(['dpkg-deb', '-f', str(package)], text=True)
            assert '\nArchitecture: all\n' in '\n' + metadata + '\n'
            assert '-powerpcspe-cross' in metadata
            r['packages'][package.name] = {'sha256': sha(package), 'metadata': metadata}
        assert r['packages']
        r['status'] = 'cross-development-packages-built-not-installed'
except Exception as error:
    r.update(status='failed', error=str(error))
    raise
finally:
    (a.output / 'receipt.json').write_text(json.dumps(r, indent=2) + '\n')
print(r['status'])
