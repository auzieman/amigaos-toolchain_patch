#!/usr/bin/env python3
"""Preinstall the selected sources' native build dependencies in a frozen root.

Uses apt on the original hash-pinned DSCs, not a hand-maintained dependency list.
The R730 host is unchanged. SPE libraries remain separate archive inputs.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
for key in ['project', 'base', 'output']:
    p.add_argument('--' + key, type=Path, required=True)
p.add_argument('--resume', action='store_true', help='Resume this job-owned template, preserving earlier attempts')
a = p.parse_args()
a.output.mkdir(exist_ok=a.resume)

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

profile = json.loads((a.project / 'profiles/images/debian-package-builder.json').read_text())
spec = json.loads((a.project / 'profiles/sbuild/libx11.json').read_text())
lockpath = a.project / 'profiles/trixie-spe-base.lock.json'
lock = json.loads(lockpath.read_text())
parent = a.base / spec['native_root_receipt']
assert sha(parent) == spec['native_root_receipt_sha256']
parent_record = json.loads(parent.read_text())
assert parent_record['status'] == 'native-buildd-root-created'
assert parent_record['base_lock_sha256'] == sha(lockpath)
archive = parent.parent / 'trixie-amd64.tar'
assert sha(archive) == parent_record['sha256']
root = a.output / 'root'
root.mkdir(exist_ok=a.resume)
r = {'status': 'preparing', 'base_lock_sha256': sha(lockpath),
     'parent_receipt_sha256': sha(parent), 'items': [], 'target_execution': False,
     'role': 'Native build dependency superset; not SPE library installation',
     'recipe_sha256': sha(Path(__file__))}
if a.resume:
    previous = json.loads((a.output / 'receipt.json').read_text())
    assert previous['base_lock_sha256'] == r['base_lock_sha256']
    assert previous['parent_receipt_sha256'] == r['parent_receipt_sha256']
    (a.output / ('prior-receipt-' + str(len(previous.get('items', []))) + '.json')).write_text(json.dumps(previous, indent=2) + '\n')
    r['items'] = previous['items']

def save():
    (a.output / 'receipt.json').write_text(json.dumps(r, indent=2) + '\n')

def run(args, name):
    with (a.output / (name + '.log')).open('w') as log:
        return subprocess.run(list(map(str, args)), stdout=log, stderr=subprocess.STDOUT).returncode

def inside(args, name):
    return run(['systemd-nspawn', '--quiet', '--register=no', '--as-pid2', '--timezone=off',
                '--directory=' + str(root), '--setenv=DEBIAN_FRONTEND=noninteractive',
                '--setenv=LC_ALL=C.UTF-8', *args], name)

try:
    save()
    if not a.resume:
        assert run(['tar', '--numeric-owner', '-xf', archive, '-C', root], 'extract') == 0
    # The parent already has signed, snapshot-only binary repositories. Add
    # source entries from the same lock for apt's source metadata needs.
    sources = root / 'etc/apt/sources.list.d/port-build-sources.list'
    sources.write_text(''.join('deb-src [check-valid-until=no] ' + x['url'] + ' ' + x['suite'] + ' main\n'
                               for x in lock['repositories']))
    (root / 'etc/apt/apt.conf.d/90port-package-cache').write_text(
        'APT::Keep-Downloaded-Packages "true";\nBinary::apt-get::APT::Keep-Downloaded-Packages "true";\n')
    if a.resume:
        assert inside(['dpkg', '--configure', '-a'], 'resume-configure') == 0
    assert inside(['apt-get', 'update'], 'apt-update') == 0
    intake = root / 'opt/port-build-inputs'
    intake.mkdir(parents=True, exist_ok=a.resume)
    for name in profile['packages']:
        if any(x['source'] == name and x['exit'] == 0 for x in r['items']):
            continue
        settings = {**profile, **profile.get('package_inputs', {}).get(name, {})}
        component = json.loads((a.project / settings['source_lock']).read_text())['components'][name]
        dsc = a.base / settings['source_cache'] / component['dsc']
        expected = next(x['sha256'] for x in component['files'] if x['filename'] == component['dsc'])
        assert sha(dsc) == expected
        shutil.copyfile(dsc, intake / dsc.name)
        # Include independent dependencies too: this is a broad tools cache,
        # not a request to compile documentation or another architecture.
        cmd = ['apt-get', '--no-remove', '--no-install-recommends', '-y',
               'build-dep', '--build-profiles=cross,nocheck', '/opt/port-build-inputs/' + dsc.name]
        r['active_source'] = name
        save()
        attempt = 1 + sum(x['source'] == name for x in r['items'])
        code = inside(cmd, name + '-' + str(attempt))
        r['items'].append({'source': name, 'version': component['version'],
                           'dsc_sha256': expected, 'exit': code})
        save()
    assert inside(['apt-get', 'check'], 'apt-check') == 0
    audit = subprocess.check_output(['chroot', str(root), 'dpkg', '--audit'], text=True)
    (a.output / 'dpkg-audit.txt').write_text(audit)
    assert not audit, audit
    manifest = subprocess.check_output(['chroot', str(root), 'dpkg-query', '-W',
        '-f=${binary:Package}\t${Version}\t${Architecture}\t${db:Status-Status}\n'], text=True)
    (a.output / 'installed.tsv').write_text(manifest)
    versions = {}
    for line in manifest.splitlines():
        name, version, architecture, status = line.split('\t')
        assert status == 'installed'
        versions[name.split(':')[0]] = version
    for name, version in lock['native_foundation'].items():
        assert versions.get(name) == version, (name, versions.get(name), version)
    r['installed_packages'] = len(versions)
    r['installed_manifest_sha256'] = sha(a.output / 'installed.tsv')
    latest = {x['source']: x for x in r['items']}
    r['failed_sources'] = [name for name, x in latest.items() if x['exit']]
    if r['failed_sources']:
        r['status'] = 'native-dependencies-installed-with-deferred-sources'
    else:
        # Package the prepared template only after all source dependency
        # installations pass. Each actual sbuild still resolves its own deps.
        assert run(['tar', '--numeric-owner', '-cf', a.output / 'trixie-amd64.tar', '-C', root, '.'], 'archive') == 0
        r.update(status='native-buildd-root-created', sha256=sha(a.output / 'trixie-amd64.tar'))
except BaseException as error:
    r.update(status='failed', error=str(error))
    raise
finally:
    save()
