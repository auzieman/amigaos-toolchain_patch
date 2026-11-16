#!/usr/bin/env python3
"""Fetch one component's source files from a reviewed lock into an sbuild source cache.

Used on a fresh build host to fill the `source_cache` directory that an
sbuild spec names. Every file is checked against the lock's size and sha256;
nothing is fetched that the lock does not list.
"""
import argparse, hashlib, json, urllib.request
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--lock', type=Path, required=True)
p.add_argument('--component', required=True)
p.add_argument('--cache', type=Path, required=True)
a = p.parse_args()
component = json.loads(a.lock.read_text())['components'][a.component]
a.cache.mkdir(parents=True, exist_ok=True)

def verified(path, entry):
    with path.open('rb') as f:
        digest = hashlib.file_digest(f, 'sha256').hexdigest()
    return path.stat().st_size == entry['size'] and digest == entry['sha256']

for entry in component['files']:
    assert Path(entry['filename']).name == entry['filename'], entry['filename']
    path = a.cache / entry['filename']
    if not path.exists():
        part = path.with_name(path.name + '.partial')
        with urllib.request.urlopen(entry['url'], timeout=60) as src, part.open('wb') as dst:
            while chunk := src.read(1 << 20):
                dst.write(chunk)
        if not verified(part, entry):
            raise SystemExit('Download mismatch: ' + entry['filename'])
        part.rename(path)
    if not verified(path, entry):
        raise SystemExit('Cached input mismatch: ' + entry['filename'])
    print('Verified', entry['filename'])
print(a.component, component['version'])
