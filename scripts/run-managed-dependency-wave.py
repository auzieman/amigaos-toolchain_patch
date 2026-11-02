#!/usr/bin/env python3
"""Prepare normal cross-build dependencies, then run one frozen serial queue.

Run on R730 under tabor-core-queue.service from a fresh metadata snapshot.
This chains explicit recipes; Debian still checks every source's dependencies.
"""
import argparse, hashlib, json, os, re, shutil, subprocess, time
from pathlib import Path
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--project', type=Path, required=True)
p.add_argument('--base', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--native-context', type=Path, required=True)
p.add_argument('--native-unit', required=True)
p.add_argument('--queue', required=True)
a = p.parse_args()
assert a.output.resolve().is_relative_to((a.base/'work').resolve())
assert (a.project/a.queue).resolve().is_relative_to(a.project/'profiles/queues')
a.output.mkdir(exist_ok=False)
sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
r = {'status': 'waiting-for-native-dependencies', 'recipe_sha256': sha(Path(__file__)),
     'commands': [], 'images': {}, 'target_installation': False, 'boot_image_ready': False}
def save():
    temp = a.output/'receipt.tmp'; temp.write_text(json.dumps(r, indent=2)+'\n')
    temp.replace(a.output/'receipt.json')
def run(cmd, name, env=None):
    r['commands'].append(list(map(str, cmd))); save()
    with (a.output/(name+'.log')).open('w') as log:
        subprocess.run(list(map(str, cmd)), env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
def build(context, parent, name, offline):
    cmd = ['docker', 'build', '--cpuset-cpus=0-3', '--memory=6g',
           '--build-arg', 'BUILD_INFRA_IMAGE='+parent, '--iidfile', str(context/'image.id')]
    if offline: cmd.append('--network=none')
    run(cmd+[str(context)], name, {**os.environ, 'DOCKER_BUILDKIT': '0'})
    image = (context/'image.id').read_text().strip()
    assert re.fullmatch(r'sha256:[0-9a-f]{64}', image)
    r['images'][name] = image; save(); return image
try:
    save()
    deadline = time.monotonic()+3600
    while not (a.native_context/'image.id').exists():
        assert time.monotonic() < deadline, 'Native dependency preparation timed out'
        assert subprocess.run(['systemctl', 'is-active', '--quiet', a.native_unit]).returncode == 0, 'Native dependency image failed'
        time.sleep(5)
    initial = (a.native_context/'image.id').read_text().strip()
    assert re.fullmatch(r'sha256:[0-9a-f]{64}', initial)
    r['images']['native-prerequisites'] = initial
    r['native_dockerfile_sha256'] = sha(a.native_context/'Dockerfile')
    r['status'] = 'installing-native-bin-nmu-tool'; save()
    context = a.output/'native-bin-nmu'; context.mkdir()
    shutil.copyfile(a.project/'docker/Dockerfile.native-bin-nmu', context/'Dockerfile')
    native = build(context, initial, 'native-bin-nmu', False)
    r['status'] = 'installing-target-development-packages'; save()
    context = a.output/'target-development'
    run(['python3', a.project/'scripts/prepare-target-build-context.py', '--base', a.base,
         '--manifest', a.project/'profiles/repositories/target-development-selinux-prerequisites.json',
         '--dockerfile', a.project/'docker/Dockerfile.target-development', '--output', context], 'prepare-target-context')
    image = build(context, native, 'target-development', True)
    run(['docker', 'run', '--rm', '--name', 'tabor-managed-default-check-002',
         '--cpus=1', '--memory=1g', '--pids-limit=64', '--network=none',
         '-v', str(a.project)+':/project:ro', '-v', str(a.base/'work')+':/work', image,
         '/project/scripts/verify-spe-managed-toolchain.py', '--output',
         '/work/'+a.output.name+'/installed-default-check'], 'installed-default-check')
    # Seal the actual produced image digest into this not-yet-running snapshot.
    # The queue records hashes of all these inputs before making any attempt.
    profile = a.project/'profiles/images/debian-package-builder.json'
    r['builder_profile_before_sha256'] = sha(profile)
    settings = json.loads(profile.read_text()); settings['image_id'] = image
    profile.write_text(json.dumps(settings, indent=2)+'\n')
    r['builder_profile_sha256'] = sha(profile)
    r['status'] = 'running-package-queue'; save()
    run(['python3', a.project/'scripts/run-core-build-queue.py', '--project', a.project,
         '--queue', a.project/a.queue, '--output', a.output/'queue'], 'queue')
    r['status'] = json.loads((a.output/'queue/receipt.json').read_text())['status']
except BaseException as e:
    r.update(status='failed', error=str(e)); raise
finally:
    save()
