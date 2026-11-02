#!/usr/bin/env python3
"""Submit one constrained, fresh Debian/SPE package build to the R730."""
import argparse, hashlib, json, re, shlex, subprocess
from pathlib import Path
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--package', required=True)
p.add_argument('--iteration', required=True)
p.add_argument('--check-dependencies-only', action='store_true')
a = p.parse_args()
assert re.fullmatch(r'[0-9]{3}', a.iteration)
project = Path(__file__).resolve().parents[1]
profile = json.loads((project / 'profiles/images/debian-package-builder.json').read_text())
assert a.package in profile['packages'], 'Package needs reviewed intake and recipe first'
profile.update(profile.get('package_inputs', {}).get(a.package, {}))
helper = project.parent / 'lab/consolidation-20261002/r730-prep-20261031'
base = profile['server_base']
queue_active = subprocess.run(['python3', str(helper / 'sudo.py'),
    'systemctl is-active --quiet tabor-core-queue.service'], capture_output=True)
assert queue_active.returncode != 0, 'The serial core queue owns package submission; add work to a later queue pass'
# Serial submission: refuse to add a second active package build.
active = subprocess.check_output(['python3', str(helper / 'sudo.py'),
    "docker ps --filter name=tabor- --format '{{.Names}}'"], text=True).strip()
assert not active, 'A package build is already active: ' + active
files = ['scripts/build-debian-package.py', profile['source_lock']]
if not profile.get('package_managed_root') and not profile.get('indep_only'):
    files.append('profiles/images/spe-bootstrap.shlibs')
series = project / 'patches' / a.package / 'series.json'
if series.exists():
    files.append(str(series.relative_to(project)))
    if series.with_name('series').exists():
        files.append(str(series.with_name('series').relative_to(project)))
    files.extend(item['path'] for item in json.loads(series.read_text())['patches'])
name = 'tabor-debian-' + a.package + '-' + a.iteration
snapshot = base + '/submissions/' + name + '/project'
subprocess.run(['python3', str(helper / 'remote.py'), shlex.join(['python3', '-c',
    'from pathlib import Path; Path(' + repr(snapshot) + ').mkdir(parents=True, exist_ok=False)'])], check=True)
digests = {}
for name in files:
    path = project / name
    relative = path.relative_to(project)
    remote = snapshot + '/' + str(relative)
    subprocess.run(['python3', str(helper / 'remote.py'),
        'mkdir -p ' + shlex.quote(str(Path(remote).parent))], check=True)
    subprocess.run(['python3', str(helper / 'remote.py'), 'cat > ' + shlex.quote(remote)],
                   input=path.read_bytes(), check=True)
    digests[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
subprocess.run(['python3', str(helper / 'remote.py'), 'cat > ' + shlex.quote(snapshot + '/submission.json')],
               input=json.dumps({'files': digests, 'settings': profile}, indent=2).encode(), check=True)
name = 'tabor-debian-' + a.package + '-' + a.iteration
command = ['docker', 'run', '-d', '--name', name, '--cpus=' + str(profile['cpus']),
           '--memory=' + profile['memory'], '--pids-limit=' + str(profile['pids_limit']),
           '--network=none']
mounts = [(snapshot, '/project'), (base + '/' + profile['source_cache'], '/cache')]
if profile.get('tools_prefix', '/tools') == '/tools':
    mounts.append((base + '/' + profile['tools'], '/tools'))
if profile.get('sysroot_prefix', '/sysroot') == '/sysroot':
    mounts.append((base + '/' + profile['sysroot'], '/sysroot'))
for source, target in mounts:
    command += ['-v', source + ':' + target + ':ro']
command += ['-v', base + '/work:/work', profile['image_id'],
            '/project/scripts/build-debian-package.py', '--project', '/project',
            '--cache', '/cache', '--tools', profile.get('tools_prefix', '/tools'), '--sysroot', profile.get('sysroot_prefix', '/sysroot'),
            '--work', '/work/debian-' + a.package + '-' + a.iteration,
            '--source-lock', profile['source_lock'], '--package', a.package,
            '--image-id', profile['image_id'], '--jobs', str(profile['cpus'])]
if a.check_dependencies_only:
    command += ['--check-dependencies-only']
if profile.get('arch_only'):
    command += ['--arch-only']
if profile.get('indep_only'):
    command += ['--indep-only']
if 'build_profiles' in profile:
    command += ['--build-profiles', profile['build_profiles']]
if profile.get('preserve_debian_version'):
    command += ['--preserve-debian-version']
if profile.get('package_managed_root'):
    command += ['--package-managed-root']
subprocess.run(['python3', str(helper / 'sudo.py'), shlex.join(command)], check=True)
print('Submitted', name, 'on R730; no local build or automatic retry')
