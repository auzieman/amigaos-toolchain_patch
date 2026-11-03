#!/usr/bin/env python3
"""Cache producer source archives identified by the frozen Debian port audit.

This performs source intake only, never changes compiler selection or builds a
candidate. Archive bytes are checked against authenticated Sources metadata.
"""
import argparse
import hashlib
import json
import lzma
import subprocess
from pathlib import Path
from debian.deb822 import Sources

p = argparse.ArgumentParser(description=__doc__)
for key in ['intake', 'source-indexes', 'cache', 'output']:
    p.add_argument('--' + key, type=Path, required=True)
a = p.parse_args()
a.output.mkdir(exist_ok=False)
a.cache.mkdir(exist_ok=True)

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

receipt = json.loads((a.intake / 'receipt.json').read_text())
assert receipt['status'] == 'dependency-producer-intake-planned'
planpath = a.intake / 'source-intake-plan.json'
assert sha(planpath) == receipt['plan_sha256']
plan = json.loads(planpath.read_text())
indexes = json.loads((a.source_indexes / 'receipt.json').read_text())
assert sha(a.source_indexes / 'receipt.json') == receipt['source_index_receipt_sha256']
selected = {}
for i, index in enumerate(indexes['source_indexes']):
    archive = a.source_indexes / (str(i) + '-Sources.xz')
    assert sha(archive) == index['sha256']
    with lzma.open(archive, 'rt') as stream:
        for source in Sources.iter_paragraphs(stream, use_apt_pkg=False):
            name = source['Package']
            if name in plan['components'] and source['Version'] == plan['components'][name]['version']:
                selected[name] = (source, index['url'].split('/dists/')[0] + '/')
assert set(selected) == set(plan['components'])
r = {'status': 'downloading', 'items': [], 'target_execution': False,
     'compiler_selection_changed': False, 'intake_receipt_sha256': sha(a.intake / 'receipt.json')}
lock = {'scope': 'Frozen dependency producer source intake; candidates, not compiler/base upgrades or accepted builds',
        'base_lock_sha256': receipt['base_lock_sha256'], 'components': {}}

def save():
    (a.output / 'receipt.json').write_text(json.dumps(r, indent=2) + '\n')
    (a.output / 'sources.lock.json').write_text(json.dumps(lock, indent=2) + '\n')

try:
    save()
    for name, (source, prefix) in sorted(selected.items()):
        r['active_source'] = name
        save()
        files = []
        for entry in source['Checksums-Sha256']:
            filename = entry['name']
            assert Path(filename).name == filename
            url = prefix + source['Directory'] + '/' + filename
            target = a.cache / filename
            if not target.exists():
                temporary = target.with_name(filename + '.partial')
                with (a.output / (name + '-download.log')).open('a') as log:
                    subprocess.run(['curl', '--fail', '--location', '--retry', '3', '--max-time', '900',
                                    '--silent', '--show-error', url, '-o', str(temporary)],
                                   stdout=log, stderr=subprocess.STDOUT, check=True)
                assert temporary.stat().st_size == int(entry['size']) and sha(temporary) == entry['sha256']
                temporary.rename(target)
            assert target.stat().st_size == int(entry['size']) and sha(target) == entry['sha256']
            files.append({'filename': filename, 'url': url, 'size': int(entry['size']), 'sha256': entry['sha256']})
        lock['components'][name] = {'version': source['Version'],
            'dsc': next(x['filename'] for x in files if x['filename'].endswith('.dsc')), 'files': files}
        r['items'].append({'source': name, 'version': source['Version'], 'files': len(files)})
        save()
    r.update(status='source-archives-cached-not-built', sources=len(r['items']),
             license_review='Original source notices retained; review debian/copyright before source modification/reuse')
except BaseException as error:
    r.update(status='failed', error=str(error))
    raise
finally:
    save()
