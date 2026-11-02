#!/usr/bin/env python3
"""R730 serial fail-forward attempts; Debian checks readiness, not this queue.

Run from a frozen project snapshot. A failed source does not stop unrelated
attempts. Nothing is installed, indexed or promoted automatically.
"""
import argparse
import fcntl
import hashlib
import json
import re
import signal
import subprocess
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--project', type=Path, required=True)
p.add_argument('--queue', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
spec = json.loads(a.queue.read_text())
profile_path = a.project / 'profiles/images/debian-package-builder.json'
profile = json.loads(profile_path.read_text())
base = Path(profile['server_base'])
assert a.output.resolve().is_relative_to((base / 'work').resolve())
lock = (base / 'work/.core-package-queue.lock').open('a')
fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
assert not subprocess.check_output(['docker', 'ps', '--filter', 'name=tabor-', '--format', '{{.Names}}'], text=True).strip(), 'Another task container is active'
a.output.mkdir(exist_ok=False)
sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
r = {'status': 'running', 'queue_sha256': sha(a.queue),
     'builder_profile_sha256': sha(profile_path), 'recipe_sha256': sha(Path(__file__)),
     'snapshot_files': {str(f.relative_to(a.project)): sha(f) for f in sorted(a.project.rglob('*')) if f.is_file()},
     'items': [], 'target_installation': False, 'boot_image_ready': False}
current = None

def save():
    temp = a.output / 'receipt.tmp'
    temp.write_text(json.dumps(r, indent=2) + '\n')
    temp.replace(a.output / 'receipt.json')
    deferred = [x for x in r['items'] if x['status'] not in ['running', 'debian-packages-built-not-target-installed', 'build-dependencies-satisfied-not-built']]
    (a.output / 'deferred.json').write_text(json.dumps(deferred, indent=2) + '\n')
    view = base / 'viewport-live-001/current.json'
    if view.parent.exists() and r['items']:
        done = sum(x['status'] == 'debian-packages-built-not-target-installed' for x in r['items'])
        ready = sum(x['status'] == 'build-dependencies-satisfied-not-built' for x in r['items'])
        view.write_text(json.dumps({
            'iteration': r['items'][-1].get('active_iteration', 'queue-starting'),
            'runtime': f'Queue: {done} built, {ready} dependency-ready only, {len(deferred)} deferred; target root unconfigured',
            'viewer': 'QEMU/noVNC stopped; this pass builds packages only'}, indent=2) + '\n')

def interrupted(signum, frame):
    raise KeyboardInterrupt()

signal.signal(signal.SIGTERM, interrupted)

def attempt(package, iteration, settings, preflight):
    global current
    assert not subprocess.check_output(['docker', 'ps', '--filter', 'name=tabor-', '--format', '{{.Names}}'], text=True).strip(), 'Another task container is active'
    suffix = ('preflight-' if preflight else '') + iteration
    work = base / 'work' / ('debian-' + package + '-' + suffix)
    assert not work.exists(), 'Existing output retained: ' + str(work)
    current = 'tabor-core-' + package + '-' + suffix
    r['items'][-1]['active_iteration'] = work.name
    save()
    command = ['docker', 'run', '--rm', '--name', current,
               '--cpus=' + str(settings['cpus']), '--memory=' + settings['memory'],
               '--pids-limit=' + str(settings['pids_limit']), '--network=none',
               '--entrypoint', 'python3']
    mounts = [(str(a.project), '/project'), (str(base / settings['source_cache']), '/cache')]
    if settings.get('tools_prefix', '/tools') == '/tools':
        mounts.append((str(base / settings['tools']), '/tools'))
    if settings.get('sysroot_prefix', '/sysroot') == '/sysroot':
        mounts.append((str(base / settings['sysroot']), '/sysroot'))
    for source, target in mounts:
        command += ['-v', source + ':' + target + ':ro']
    command += ['-v', str(base / 'work') + ':/work', settings['image_id'],
                '/project/scripts/build-debian-package.py', '--project', '/project',
                '--cache', '/cache', '--tools', settings.get('tools_prefix', '/tools'),
                '--sysroot', settings.get('sysroot_prefix', '/sysroot'), '--work', '/work/' + work.name,
                '--source-lock', settings['source_lock'], '--package', package,
                '--image-id', settings['image_id'], '--jobs', str(settings['cpus'])]
    if preflight:
        command.append('--check-dependencies-only')
    for key, flag in [('arch_only', '--arch-only'), ('indep_only', '--indep-only')]:
        if settings.get(key):
            command.append(flag)
    if 'build_profiles' in settings:
        command += ['--build-profiles', settings['build_profiles']]
    if settings.get('binary_nmu'):
        command += ['--binary-nmu', str(settings['binary_nmu'])]
    if settings.get('preserve_debian_version'):
        command += ['--preserve-debian-version']
    if settings.get('package_managed_root'):
        command += ['--package-managed-root']
    with (a.output / (package + '-' + suffix + '.log')).open('w') as log:
        try:
            t = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT,
                               timeout=spec.get('timeout_seconds', 7200))
        except (subprocess.TimeoutExpired, KeyboardInterrupt):
            subprocess.run(['docker', 'kill', current], capture_output=True, timeout=30)
            raise
        finally:
            current = None
    receipt = work / 'receipt.json'
    result = {'exit': t.returncode, 'receipt': str(receipt), 'phase': 'preflight' if preflight else 'build'}
    if receipt.exists():
        result.update(receipt_sha256=sha(receipt), status=json.loads(receipt.read_text())['status'])
    else:
        result['status'] = 'infrastructure-failed-no-receipt'
    log = work / 'build.log'
    if log.exists():
        with log.open('rb') as f:
            f.seek(max(0, log.stat().st_size - 16000))
            lines = f.read().decode(errors='replace').splitlines()
        result['diagnostic_tail'] = [line[:300] for line in lines[-12:]]
        result['unmet_dependencies'] = [line[:2000] for line in lines if 'unmet build dependencies:' in line]
    return result

try:
    save()
    for item in spec['attempts']:
        package, iteration = item['package'], item['iteration']
        assert re.fullmatch(r'[a-z0-9][a-z0-9+.-]*', package)
        assert re.fullmatch(r'[0-9]{3}', iteration)
        record = {'package': package, 'iteration': iteration, 'status': 'running'}
        r['items'].append(record); save()
        try:
            assert package in profile['packages']
            settings = {**profile, **profile.get('package_inputs', {}).get(package, {})}
            assert settings['image_id'].startswith('sha256:') and len(settings['image_id']) == 71
            preflight = attempt(package, iteration, settings, True)
            record['preflight'] = preflight
            if preflight['exit'] or preflight['status'] != 'build-dependencies-satisfied-not-built':
                record['status'] = preflight['status']
            elif item.get('preflight_only', spec.get('preflight_only', False)):
                record['status'] = 'build-dependencies-satisfied-not-built'
            else:
                record['build'] = attempt(package, iteration, settings, False)
                record['status'] = record['build']['status']
        except Exception as error:
            record.update(status='attempt-failed', error=str(error))
        save()
        print(package + ': ' + record['status'], flush=True)
    r['status'] = 'completed' if all(x['status'] in ['debian-packages-built-not-target-installed', 'build-dependencies-satisfied-not-built'] for x in r['items']) else 'completed-with-deferred-items'
except BaseException:
    r['status'] = 'interrupted'
    if r['items'] and r['items'][-1]['status'] == 'running':
        r['items'][-1]['status'] = 'interrupted'
    raise
finally:
    save()
