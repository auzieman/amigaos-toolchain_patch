#!/usr/bin/env python3
"""Expand port source discovery from Debian dose failure chains and signed indexes.

Metadata only. No synthetic target packages or claims of build readiness. The
native binary index maps binary names/Provides to producer sources; all source
versions come from the frozen authenticated Sources indexes.
"""
import argparse
import hashlib
import json
import lzma
import subprocess
from pathlib import Path
from debian.deb822 import Packages, Sources, PkgRelation
from debian.debian_support import Version
import yaml

p = argparse.ArgumentParser(description=__doc__)
for key in ['audit', 'source_indexes', 'output']:
    p.add_argument('--' + key.replace('_', '-'), type=Path, required=True)
p.add_argument('--only-producers',nargs='+',help='Review-bounded intake of these producer sources only')
p.add_argument('--cache',type=Path,help='Cache archives after bounded producer review')
p.add_argument('--cache-output',type=Path)
a = p.parse_args()
a.output.mkdir(exist_ok=False)

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

parent = json.loads((a.audit / 'receipt.json').read_text())
indexes = json.loads((a.source_indexes / 'receipt.json').read_text())
assert parent['status'] == 'debian-dependency-audit-completed'
assert indexes['base_lock_sha256'] == parent['base_lock_sha256']
native = a.audit / 'NativePackages'
assert sha(native) == parent['native_packages_sha256']
r = {'status': 'preparing', 'base_lock_sha256': parent['base_lock_sha256'],
     'audit_receipt_sha256': sha(a.audit / 'receipt.json'),
     'source_index_receipt_sha256': sha(a.source_indexes / 'receipt.json'),
     'target_execution': False, 'sources_built': False, 'waves': [],
     'native_role_review': [], 'unmapped': [], 'producers': {}}
try:
    available = {}
    for i, entry in enumerate(indexes['source_indexes']):
        archive = a.source_indexes / (str(i) + '-Sources.xz')
        assert sha(archive) == entry['sha256']
        with lzma.open(archive, 'rt') as stream:
            for source in Sources.iter_paragraphs(stream, use_apt_pkg=False):
                name = source['Package']
                if name not in available or Version(source['Version']) > Version(available[name]['Version']):
                    available[name] = source
    providers = {}
    with native.open() as stream:
        for binary in Packages.iter_paragraphs(stream, use_apt_pkg=False):
            source = binary.get('Source', binary['Package']).split()[0]
            names = [binary['Package']]
            for group in (PkgRelation.parse_relations(binary['Provides']) if binary.get('Provides') else []):
                names.extend(x['name'] for x in group)
            for name in names:
                providers.setdefault(name, set()).add(source)
    with (a.audit / 'Sources').open() as stream:
        selected = {s['Package']: s for s in Sources.iter_paragraphs(stream, use_apt_pkg=False)}
    original = set(selected)
    for wave in range(1, len(available) + 1):
        sources = a.output / ('Sources-' + str(wave))
        sources.write_text(''.join(str(s) + '\n' for s in selected.values()))
        reportpath = a.output / ('dose-' + str(wave) + '.yaml')
        cmd = ['dose-builddebcheck', '--deb-native-arch=amd64', '--deb-host-arch=powerpcspe',
               '--deb-profiles=cross,nocheck', '--deb-drop-b-d-indep', '--deb-emulate-sbuild',
               '--failures', '--explain', str(native), str(a.audit / 'SpePackages'), str(sources)]
        if wave == 1:
            original_report = a.audit / 'dependency-report.yaml'
            assert sha(original_report) == parent['report_sha256']
            reportpath.write_bytes(original_report.read_bytes())
            report = yaml.load(original_report.read_text(), Loader=yaml.BaseLoader)
        else:
            with reportpath.open('w') as out, (a.output / ('dose-' + str(wave) + '.log')).open('w') as log:
                code = subprocess.run(cmd, stdout=out, stderr=log).returncode
            assert code in [0, 1]
            report = yaml.load(reportpath.read_text(), Loader=yaml.BaseLoader)
        new = set()
        def visit(node):
            if isinstance(node, dict):
                relation = node.get('unsat-dependency')
                if relation:
                    for group in PkgRelation.parse_relations(relation):
                        for item in group:
                            if item.get('archqual') != 'powerpcspe':
                                r['native_role_review'].append(relation)
                                continue
                            matches = providers.get(item['name'], set())
                            if not matches:
                                r['unmapped'].append(relation)
                            for producer in matches:
                                if a.only_producers and producer not in a.only_producers:
                                    continue
                                if producer not in available:
                                    r['unmapped'].append(relation + ' -> ' + producer)
                                    continue
                                if producer not in original:
                                    value = r['producers'].setdefault(producer, {
                                        'version': available[producer]['Version'],
                                        'binary_requirements': []})
                                    value['binary_requirements'].append(relation)
                                if producer not in selected:
                                    new.add(producer)
                for value in node.values():
                    visit(value)
            elif isinstance(node, list):
                for value in node:
                    visit(value)
        visit(report)
        r['waves'].append({'wave': wave, 'source_count': len(selected),
                           'new_producers': sorted(new), 'report_sha256': sha(reportpath)})
        if not new:
            break
        for name in sorted(new):
            selected[name] = available[name]
        if a.only_producers:
            break
    for value in r['producers'].values():
        value['binary_requirements'] = sorted(set(value['binary_requirements']))
    r['native_role_review'] = sorted(set(r['native_role_review']))
    r['unmapped'] = sorted(set(r['unmapped']))
    plan = {'scope': 'Frozen port dependency producer intake; metadata discovery, not build readiness',
            'components': {name: {'version': x['version'],
                'reason': 'Debian solver missing target dependency: ' + ', '.join(x['binary_requirements'])}
                for name, x in sorted(r['producers'].items())}}
    (a.output / 'source-intake-plan.json').write_text(json.dumps(plan, indent=2) + '\n')
    (a.output / 'candidate-Sources').write_text(''.join(str(selected[n]) + '\n' for n in sorted(set(selected) - original)))
    r.update(status='dependency-producer-intake-planned', discovered_sources=len(plan['components']),
             limitation='Solver failures may expose only one missing relation per source. Re-evaluate after new packages; not proof of complete closure or runtime readiness.',
             plan_sha256=sha(a.output / 'source-intake-plan.json'))
except Exception as error:
    r.update(status='failed',error=str(error))
    raise
finally:
    (a.output / 'receipt.json').write_text(json.dumps(r, indent=2) + '\n')
if a.cache:
    assert a.only_producers and a.cache_output, 'Archive intake requires an explicit reviewed producer list and output'
    subprocess.run(['python3', str(Path(__file__).with_name('cache-port-dependency-sources.py')),
        '--intake', str(a.output), '--source-indexes', str(a.source_indexes),
        '--cache', str(a.cache), '--output', str(a.cache_output)], check=True)
