#!/usr/bin/env python3
"""Read-only Debian installation gate; run on the builder against an installed root.

This does not execute maintainer scripts or treat custom bundle packages as a
substitute for the required Debian binary packages. Choose names matching the
pinned source packages' actual binary-package split.
"""
import argparse, hashlib, json, subprocess
from pathlib import Path
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--root', type=Path, required=True)
p.add_argument('--require', action='append', required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
assert not a.output.exists(), 'Use a fresh evidence file'
db = a.root / 'var/lib/dpkg'
query = subprocess.run(['dpkg-query', '--admindir=' + str(db), '-W',
                        '-f=${Package}\t${Status}\n'], capture_output=True, text=True)
installed = dict(line.split('\t', 1) for line in query.stdout.splitlines())
missing = [name for name in a.require if installed.get(name) != 'install ok installed']
metadata = {}
for directory in ['info', 'updates', 'triggers']:
    folder = db / directory
    if folder.exists():
        for item in sorted(folder.iterdir()):
            if item.is_file():
                metadata[str(item.relative_to(db))] = hashlib.sha256(item.read_bytes()).hexdigest()
result = {'status': 'pass' if query.returncode == 0 and not missing else 'fail',
          'required': a.require, 'missing_or_unconfigured': missing,
          'package_states': installed, 'package_metadata_sha256': metadata,
          'scope': 'Package configuration state only; runtime/service/ABI tests are separate',
          'maintainer_scripts_executed_by_this_audit': False}
a.output.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'status': result['status'], 'missing_or_unconfigured': missing}))
raise SystemExit(0 if result['status'] == 'pass' else 1)
