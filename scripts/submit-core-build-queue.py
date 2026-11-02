#!/usr/bin/env python3
"""Freeze recipe inputs and start one serial fail-forward queue on the R730."""
import argparse, io, json, re, shlex, subprocess, tarfile
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--queue', required=True, help='Project-relative reviewed queue JSON')
p.add_argument('--run-id', required=True)
p.add_argument('--prepare-managed-root', action='store_true', help='Chain reviewed native/target dependency installation before the frozen queue')
p.add_argument('--native-context', help='Server context of the already-running native dependency image build')
p.add_argument('--native-unit', help='Server systemd unit preparing that image')
p.add_argument('--expected-image', help='Refuse submission if the selected build-root digest differs')
a = p.parse_args()
assert bool(a.native_context) == bool(a.native_unit) == a.prepare_managed_root
if a.native_unit:
    assert re.fullmatch(r'[a-z0-9.-]+', a.native_unit)
assert re.fullmatch(r'[a-z0-9][a-z0-9-]+', a.run_id)
project = Path(__file__).resolve().parents[1]
queue = (project / a.queue).resolve()
assert queue.is_relative_to(project / 'profiles/queues')
assert json.loads(queue.read_text())['attempts']
profile = json.loads((project / 'profiles/images/debian-package-builder.json').read_text())
if a.expected_image:
    assert profile['image_id'] == a.expected_image, 'Selected build root differs from the explicitly expected digest'
base = profile['server_base']
helper = project.parent / 'lab/consolidation-20261002/r730-prep-20261031'
def remote(command, root=False, **kw):
    return subprocess.run(['python3', str(helper / ('sudo.py' if root else 'remote.py')), command], check=True, **kw)
assert subprocess.run(['python3', str(helper / 'sudo.py'),
    'systemctl is-active --quiet tabor-core-queue.service'], capture_output=True).returncode != 0
active = subprocess.check_output(['python3', str(helper / 'sudo.py'),
    "docker ps --filter name=tabor- --format '{{.Names}}'"], text=True).strip()
assert not active, 'Another task build is active: ' + active
snapshot = base + '/submissions/' + a.run_id + '/project'
remote(shlex.join(['python3', '-c',
    'from pathlib import Path; Path(' + repr(snapshot) + ').mkdir(parents=True, exist_ok=False)']))
# Recipe metadata only, uncompressed and single-threaded. Full source archives,
# compilation, image assembly and target execution stay on the server.
stream = io.BytesIO()
with tarfile.open(fileobj=stream, mode='w') as tar:
    for directory in ['scripts', 'profiles', 'patches', 'docker', 'packaging']:
        for path in sorted((project / directory).rglob('*')):
            if path.is_file() and not path.is_symlink() and '__pycache__' not in path.parts:
                tar.add(path, arcname=str(path.relative_to(project)), recursive=False)
remote(shlex.join(['tar', '--no-same-owner', '-xf', '-', '-C', snapshot]), input=stream.getvalue())
runner = 'run-managed-dependency-wave.py' if a.prepare_managed_root else 'run-core-build-queue.py'
command = ['systemd-run', '--unit=tabor-core-queue', '--collect',
    '--description=Tabor serial powerpcspe package queue',
    '/usr/bin/python3', snapshot + '/scripts/' + runner,
    '--project', snapshot, '--queue', (str(queue.relative_to(project)) if a.prepare_managed_root else snapshot + '/' + str(queue.relative_to(project))),
    '--output', base + '/work/' + a.run_id]
if a.prepare_managed_root:
    assert a.native_context.startswith(base + '/submissions/')
    command += ['--base', base, '--native-context', a.native_context, '--native-unit', a.native_unit]
remote(shlex.join(command), root=True)
print('Submitted serial queue', a.run_id, 'on R730; no automatic artifact promotion')
