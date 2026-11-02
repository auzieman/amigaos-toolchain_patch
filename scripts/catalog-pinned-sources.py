#!/usr/bin/env python3
"""Audit all pinned Debian sources/cache inputs against the real archive receipts.

This inventories inputs and evidence; Debian dependency checks remain the solver.
"""
import argparse, hashlib, json, re
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
for n in ['project', 'base', 'archive', 'output']:
    p.add_argument('--' + n, type=Path, required=True)
a = p.parse_args(); a.output.mkdir(exist_ok=False)
def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        while data := f.read(1024 * 1024): h.update(data)
    return h.hexdigest()
archive = json.loads(a.archive.read_text())
built = {}
for item in archive['inputs']:
    path = a.base / item['receipt']; assert sha(path) == item['receipt_sha256']
    r = json.loads(path.read_text())
    if 'package' in r:
        built.setdefault(r['package'], []).append(item['receipt'])
sources = {}; unavailable = []
caches = sorted(x for x in a.base.iterdir() if x.is_dir() and 'cache' in x.name)
for lock in sorted((a.project / 'profiles').glob('*lock.json')):
    obj = json.loads(lock.read_text())
    entries = obj.get('components', {})
    if obj.get('dsc'):
        entries = {obj.get('component', lock.name.split('.')[0]): obj}
    for key, entry in entries.items():
        if not isinstance(entry, dict) or not entry.get('dsc'): continue
        candidates = [c for c in caches if (c / entry['dsc']).exists()]
        if not candidates:
            unavailable.append({'key': key, 'lock': str(lock.relative_to(a.project)), 'reason': 'DSC not cached'})
            continue
        cache = candidates[0]
        invalid = []
        for f in entry['files']:
            path = cache / f['filename']
            if not path.is_file() or path.stat().st_size != f['size'] or sha(path) != f['sha256']:
                invalid.append(f['filename'])
        if invalid:
            unavailable.append({'key': key, 'lock': str(lock.relative_to(a.project)), 'invalid_inputs': invalid})
            continue
        dsc = (cache / entry['dsc']).read_text()
        source = re.search(r'^Source: (.+)$', dsc, re.M)[1].strip()
        architecture = re.search(r'^Architecture: (.+)$', dsc, re.M)[1].strip()
        binaries = re.search(r'^Binary: (.+(?:\n[ \t].+)*)', dsc, re.M)[1]
        row = {'source': source, 'component_key': key, 'version': entry['version'],
               'origin_lock': str(lock.relative_to(a.project)), 'source_cache': cache.name,
               'architecture': architecture, 'binary_packages': [x.strip() for x in binaries.replace('\n', '').split(',')],
               'inputs_sha256_verified': True, 'entry': entry,
               'existing_build_receipts': built.get(source, built.get(key, [])),
               'route': 'dedicated-kernel' if source == 'linux' else 'debian-package'}
        if source in sources:
            # Never silently choose between different pinned source revisions.
            old = sources[source]
            if old['version'] != row['version'] or old['entry']['files'] != entry['files']:
                unavailable.append({'source': source, 'reason': 'Conflicting pins require review', 'lock': row['origin_lock']})
            continue
        sources[source] = row
result = {'scope': 'Verified cached/pinned source coverage, not full VM132 closure',
          'source_count': len(sources), 'sources': sources, 'unavailable_or_conflicting': unavailable,
          'archive_manifest_sha256': sha(a.archive), 'recipe_sha256': sha(Path(__file__))}
(a.output / 'catalog.json').write_text(json.dumps(result, indent=2) + '\n')
normalized = {'scope': result['scope'], 'components': {k: v['entry'] for k,v in sources.items()}}
(a.output / 'normalized.lock.json').write_text(json.dumps(normalized, indent=2) + '\n')
print(json.dumps({'verified_sources': len(sources), 'already_have_artifacts': sum(bool(v['existing_build_receipts']) for v in sources.values()), 'review_entries': len(unavailable)}))
