#!/usr/bin/env python3
"""Submit one constrained, fresh Debian/SPE package build to the R730."""
import argparse, json, re, shlex, subprocess
from pathlib import Path
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--package', required=True)
p.add_argument('--iteration', required=True)
a = p.parse_args()
assert re.fullmatch(r'[0-9]{3}', a.iteration)
project = Path(__file__).resolve().parents[1]
profile = json.loads((project / 'profiles/images/debian-package-builder.json').read_text())
assert a.package in profile['packages'], 'Package needs reviewed intake and recipe first'
profile.update(profile.get('package_inputs', {}).get(a.package, {}))
helper = project.parent / 'lab/consolidation-20261002/r730-prep-20261031'
base = profile['server_base']
# Serial submission: refuse to add a second active package build.
active = subprocess.check_output(['python3', str(helper / 'sudo.py'),
    "docker ps --filter name=tabor- --format '{{.Names}}'"], text=True).strip()
assert not active, 'A package build is already active: ' + active
files = ['scripts/build-debian-package.py', profile['source_lock'],
         'profiles/images/spe-bootstrap.shlibs']
series = project / 'patches' / a.package / 'series.json'
if series.exists():
    files.append(str(series.relative_to(project)))
    files.extend(item['path'] for item in json.loads(series.read_text())['patches'])
for name in files:
    path = project / name
    relative = path.relative_to(project)
    remote = base + '/project/' + str(relative)
    subprocess.run(['python3', str(helper / 'remote.py'),
        'mkdir -p ' + shlex.quote(str(Path(remote).parent))], check=True)
    subprocess.run(['python3', str(helper / 'remote.py'), 'cat > ' + shlex.quote(remote)],
                   input=path.read_bytes(), check=True)
name = 'tabor-debian-' + a.package + '-' + a.iteration
command = ['docker', 'run', '-d', '--name', name, '--cpus=' + str(profile['cpus']),
           '--memory=' + profile['memory'], '--pids-limit=' + str(profile['pids_limit']),
           '--network=none']
for source, target in [('project', '/project'), (profile['source_cache'], '/cache'),
                        (profile['tools'], '/tools'), (profile['sysroot'], '/sysroot')]:
    command += ['-v', base + '/' + source + ':' + target + ':ro']
command += ['-v', base + '/work:/work', profile['image_id'],
            '/project/scripts/build-debian-package.py', '--project', '/project',
            '--cache', '/cache', '--tools', '/tools', '--sysroot', '/sysroot',
            '--work', '/work/debian-' + a.package + '-' + a.iteration,
            '--source-lock', profile['source_lock'], '--package', a.package,
            '--image-id', profile['image_id'], '--jobs', str(profile['cpus'])]
subprocess.run(['python3', str(helper / 'sudo.py'), shlex.join(command)], check=True)
print('Submitted', name, 'on R730; no local build or automatic retry')
