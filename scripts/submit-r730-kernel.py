#!/usr/bin/env python3
"""Submit one fresh constrained QEMU/A1222 kernel iteration to R730."""
import argparse, re, shlex, subprocess
from pathlib import Path
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--kernel-profile', choices=['qemu-live', 'tabor-live'], required=True)
p.add_argument('--iteration', required=True)
a = p.parse_args(); assert re.fullmatch('[0-9]{3}', a.iteration)
project = Path(__file__).resolve().parents[1]
helper = project.parent / 'lab/consolidation-20261002/r730-prep-20261031'
base = '/srv/data1/tabor-build/linux-live-001'
image = 'sha256:2781e11839beffa351f8c411d71b7e2bd1ae0336d24c60b407778c3350dd9da0'
active = subprocess.check_output(['python3', str(helper / 'sudo.py'),
    "docker ps --filter name=tabor- --format '{{.Names}}'"], text=True).strip()
assert not active, 'Wait for the active Tabor job: ' + active
files = ['scripts/debian-iterate.py', 'profiles/debian-trixie.lock.json',
         'profiles/qemu/e500v2-live.config', 'profiles/images/tabor-live-kernel.config',
         'patches/linux/series']
for line in (project / 'patches/linux/series').read_text().splitlines():
    name = line.split('#', 1)[0].strip()
    if name:
        assert Path(name).name == name
        files.append('patches/linux/' + name)
for name in files:
    remote = base + '/project/' + name
    subprocess.run(['python3', str(helper / 'remote.py'),
                    'cat > ' + shlex.quote(remote)], input=(project / name).read_bytes(), check=True)
output = a.kernel_profile + '-' + a.iteration
command = ['docker', 'run', '-d', '--name', 'tabor-kernel-' + output,
           '--cpus=4', '--memory=6g', '--pids-limit=256', '--network=none',
           '--entrypoint', 'python3', '-v', base + '/project:/project:ro',
           '-v', base + '/tabor-source-cache:/cache:ro', '-v', base + '/work:/work',
           image, '/project/scripts/debian-iterate.py', '--component', 'linux',
           '--mode', 'build', '--kernel-profile', a.kernel_profile,
           '--project', '/project', '--cache', '/cache', '--work', '/work/' + output,
           '--image-id', image, '--jobs', '4']
subprocess.run(['python3', str(helper / 'sudo.py'), shlex.join(command)], check=True)
print('Submitted', output, 'on R730, 4CPU/6GiB; no workstation build')
