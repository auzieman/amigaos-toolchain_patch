#!/usr/bin/env python3
"""Run reviewed source preparation, Debian audits, builds and fallout reporting.

Debian dose/sbuild/apt own dependency semantics. This script owns stage order,
resource bounds, accepted-build reuse and retained evidence only.
"""
import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
for name in ['project', 'base', 'plan', 'output', 'native-audit']:
    p.add_argument('--' + name, type=Path, required=True)
p.add_argument('--after-receipt',type=Path,help='Wait for a previous scripted round, without overlapping package workers')
a = p.parse_args()
assert a.output.resolve().is_relative_to((a.base / 'work').resolve())
a.output.mkdir(exist_ok=False)
plan = json.loads(a.plan.read_text())
registry = json.loads((a.project / plan['registry']).read_text())['packages']
scope = json.loads((a.project / 'profiles/port-build-scope.json').read_text())
profile = json.loads((a.project / 'profiles/images/debian-package-builder.json').read_text())
defaults = json.loads((a.project / plan['defaults']).read_text())

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

r = {'status': 'running', 'plan_sha256': sha(a.plan), 'stages': [],
     'source_preparation': {}, 'reused': [], 'fallout': [],
     'target_execution': False, 'target_image_accepted': False}
prefix = a.output.name

def save():
    (a.output / 'receipt.json').write_text(json.dumps(r, indent=2) + '\n')
    (a.output / 'fallout.json').write_text(json.dumps(r['fallout'], indent=2) + '\n')

def job(args, name, memory='3G'):
    with (a.output / (name + '.log')).open('w') as log:
        return subprocess.run(['systemd-run', '--quiet', '--wait', '--pipe', '--collect',
            '--unit=' + prefix + '-' + name, '--property=CPUQuota=100%',
            '--property=MemoryMax=' + memory, '--property=TasksMax=256',
            *map(str, args)], stdout=log, stderr=subprocess.STDOUT).returncode

native_receipt=json.loads((a.native_audit/'receipt.json').read_text())
assert sha(a.native_audit/'NativePackages')==native_receipt['native_packages_sha256']
# Binary revisions are explicit reviewed sbuild requests, never inferred policy.

def already_built(name, bootstrap):
    options = registry.get(name, {})
    if not bootstrap and name in plan.get('force_full_rebuild', []):
        return False
    settings = {**profile, **profile.get('package_inputs', {}).get(name, {})}
    component = json.loads((a.project / settings['source_lock']).read_text())['components'][name]
    profiles = options.get('build_profiles', 'cross,nocheck')
    if bootstrap:
        profiles = options.get('bootstrap_profiles', profiles)
    patch = None
    version = component['version']
    if options.get('spec'):
        spec = json.loads((a.project / options['spec']).read_text())
        patch = spec.get('source_patch')
        if patch:
            version = patch['version']
    for path in a.base.glob('work/*/receipt.json'):
        try:
            record = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        if record.get('status') != 'debian-packages-built-not-target-installed' or record.get('package') != name:
            continue
        if record.get('binary_nmu', 0) != options.get('binary_nmu', 0):
            continue
        if record.get('source_version') != version or record.get('host_architecture') != 'powerpcspe':
            continue
        if set(record.get('build_profiles', 'cross,nocheck').split(',')) != set(profiles.split(',')):
            continue
        if patch and record.get('patched_source', {}).get('patch_sha256') != patch['sha256']:
            continue
        inspection = path.parent / 'payload-inspection.json'
        if not inspection.exists() or record.get('payload_inspection_sha256') != sha(inspection):
            continue
        r['reused'].append({'package': name, 'receipt': str(path), 'bootstrap_phase': bootstrap})
        return True
    return False

try:
    if a.after_receipt:
        r['status']='waiting-for-prior-run';save()
        deadline=time.monotonic()+12*3600
        while True:
            previous=json.loads(a.after_receipt.read_text())
            if previous['status'] in ['selected-build-stages-completed','completed-with-fallout']:
                break
            assert previous['status'] in ['running','waiting-for-prior-run'], 'Prior pipeline needs infrastructure review'
            assert time.monotonic()<deadline, 'Prior pipeline wait timed out'
            time.sleep(10)
        r['status']='running'
    historical_failures = []
    r['prior_failure_receipts'] = []
    for receipt in sorted((a.base / 'work').glob('port-pipeline-*/receipt.json')):
        if receipt == a.output / 'receipt.json':
            continue
        record = json.loads(receipt.read_text())
        if record.get('status') not in ['selected-build-stages-completed', 'completed-with-fallout']:
            continue
        failures = [x for x in record.get('fallout', []) if x.get('input_fingerprint')]
        if failures:
            historical_failures.extend(failures)
            r['prior_failure_receipts'].append({'receipt':str(receipt), 'sha256':sha(receipt)})
    save()
    prepared = {}
    excluded = set(scope['deferred_candidates'])
    for name in plan.get('require_patched_sources', []):
        if not registry.get(name, {}).get('spec'):
            excluded.add(name)
            r['fallout'].append({'package': name, 'stage': 'source-configuration',
                'kind': 'patched-source-spec-required',
                'reason': 'Preserve the accepted patched foundation; do not submit the vanilla source for a required SPE restoration.'})
    # Prepare reviewed changes before checking dependencies: the solver sees
    # the actual resulting DSC, including changed Debian Build-Depends.
    for name, options in registry.items():
        if not options.get('spec') or name in excluded:
            continue
        spec = json.loads((a.project / options['spec']).read_text())
        spec.update(prepare_only=True, extra_receipts=[], native_toolchain_inputs=[],
            native_root_receipt='work/frozen-buildd-root-002/receipt.json',
            native_root_receipt_sha256='e8fd69ee8fbf57c3c7a37dc8d4864aecfac0131e65577902ff6efa2598877f16')
        path = a.output / ('prepare-' + name + '.json')
        path.write_text(json.dumps(spec, indent=2) + '\n')
        work = a.base / 'work' / (prefix + '-source-' + name)
        code = job(['python3', a.project / 'scripts/run-sbuild-package.py',
            '--project', a.project, '--base', a.base, '--spec', path, '--output', work], 'prepare-' + name)
        if code:
            excluded.add(name)
            r['fallout'].append({'package': name, 'stage': 'source-preparation', 'work': str(work)})
        else:
            receipt = work / 'receipt.json'
            assert json.loads(receipt.read_text())['status'] == 'debian-source-prepared-not-built'
            prepared[name] = {'receipt': str(receipt.relative_to(a.base)), 'receipt_sha256': sha(receipt)}
        r['source_preparation'][name]={'work': str(work), 'status': 'failed' if code else 'prepared'}
        save()
    prepared_path = a.output / 'prepared-sources.json'
    prepared_path.write_text(json.dumps(prepared, indent=2) + '\n')
    previous_audit = a.native_audit
    # Genuine binary-only rebuilds precede consumers that must coinstall with
    # native Multi-Arch:same libraries already present in the broad template.
    binary_rebuilds=[]
    for name in dict.fromkeys(plan.get('bootstrap_packages', []) + plan['packages']):
        if registry.get(name,{}).get('binary_nmu',0):
            binary_rebuilds.append(name)
    for stage, bootstrap in [('binary-rebuilds', False), ('base-libraries', True), ('desktop-services', False)]:
        names = binary_rebuilds if stage=='binary-rebuilds' else (plan.get('bootstrap_packages', []) if bootstrap else plan['packages'])
        names = [n for n in names if n not in excluded and not already_built(n, bootstrap)]
        audit = a.base / 'work' / (prefix + '-' + stage + '-audit')
        cmd = ['python3', a.project / 'scripts/audit-sbuild-dependencies.py',
            '--project', a.project, '--base', a.base, '--output', audit,
            '--reuse-native-audit', previous_audit, '--registry', a.project / plan['registry'],
            '--prepared-sources', prepared_path]
        if bootstrap:
            cmd.append('--bootstrap')
        assert job(cmd, stage + '-audit') == 0, 'Debian dependency audit failed'
        batch = dict(plan, packages=names, initial_audit=str(audit.relative_to(a.base)),
            initial_audit_sha256=sha(audit / 'receipt.json'), bootstrap=bootstrap,
            prepared_sources=str(prepared_path.relative_to(a.base)),
            run_prefix=prefix + '-' + stage, unit_prefix=prefix + '-' + stage + '-build')
        batch['prior_failures']=historical_failures + [x for x in r['fallout'] if x.get('input_fingerprint')]
        batch_path = a.output / (stage + '-plan.json')
        batch_path.write_text(json.dumps(batch, indent=2) + '\n')
        work = a.base / 'work' / (prefix + '-' + stage)
        code = job(['python3', a.project / 'scripts/run-ready-sbuild-batch.py',
            '--project', a.project, '--base', a.base, '--plan', batch_path, '--output', work], stage + '-batch', '1G')
        assert code == 0, 'Batch controller infrastructure failed'
        result = json.loads((work / 'receipt.json').read_text())
        r['stages'].append({'stage': stage, 'work': str(work), 'status': result['status']})
        for item in result['items']:
            if item['status'] != 'debian-packages-built-not-target-installed':
                r['fallout'].append({'stage': stage, **item})
        for item in result.get('blocked', []):
            r['fallout'].append({'stage': stage, 'package': item['package'], 'kind': 'debian-dependency-blocked', 'reasons': item.get('reasons')})
        if result.get('audits'):
            previous_audit = Path(result['audits'][-1]['path'])
        else:
            previous_audit = audit
        save()
    r['status'] = 'completed-with-fallout' if r['fallout'] else 'selected-build-stages-completed'
except Exception as error:
    r.update(status='infrastructure-failed', error=str(error))
    raise
finally:
    save()
