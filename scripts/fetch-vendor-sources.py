#!/usr/bin/env python3
"""Fetch exact vendor reference revisions, or check existing clean copies."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--check-only', action='store_true')
a = p.parse_args()
lock = json.loads((root/'profiles/vendor-sources.lock.json').read_text())
for item in lock['sources']:
    name = item['directory']
    if Path(name).name != name:
        raise SystemExit('Invalid source directory')
    target = root/'sources/vendor'/name
    def git(*args):
        return subprocess.check_output(['git', '-C', str(target), *args], text=True).strip()
    if not target.exists():
        if a.check_only:
            raise SystemExit('Missing vendor source: '+name)
        target.mkdir(parents=True)
        subprocess.run(['git', 'init', '-q', str(target)], check=True)
        subprocess.run(['git', '-C', str(target), 'remote', 'add', 'origin', item['url']], check=True)
        subprocess.run(['git', '-C', str(target), 'fetch', '--depth', '1', 'origin', item['commit']], check=True)
        subprocess.run(['git', '-C', str(target), 'checkout', '--detach', item['commit']], check=True)
    if git('rev-parse', 'HEAD') != item['commit'] or git('status', '--porcelain'):
        raise SystemExit('Changed vendor source; preserve and inspect: '+name)
    if git('rev-parse', 'HEAD^{tree}') != item['tree']:
        raise SystemExit('Tree mismatch: '+name)
    for file, expected in item['inspected_file_sha256'].items():
        actual = hashlib.sha256((target/file).read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit('Inspected file mismatch: '+name+'/'+file)
    print('Verified '+name+' @ '+item['commit'])
