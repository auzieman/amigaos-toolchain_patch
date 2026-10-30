#!/usr/bin/env python3
"""Prepare an immutable kernel input in fresh storage; optionally cross-build it."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def within(root, name):
    p = (root / name).resolve()
    if not p.is_relative_to(root.resolve()):
        raise ValueError('Path outside input/output root: ' + name)
    return p


def execute(args):
    profile = json.loads(args.profile.read_text())
    if not re.fullmatch(r'[0-9a-f]{40}', profile['commit']):
        raise ValueError('Expected immutable 40-digit source commit')
    if not re.search(r'(?:^|@)sha256:[0-9a-f]{64}$', args.image_id):
        raise ValueError('Expected digest-identified compiler image')
    if args.jobs < 1 or args.jobs > 32:
        raise ValueError('jobs must be between 1 and 32')
    inputs = args.inputs.resolve()
    work = args.work.resolve()
    if work.is_relative_to(inputs) or inputs.is_relative_to(work):
        raise ValueError('Work and input trees must be independent')
    work.mkdir(parents=True, exist_ok=False)
    receipt = {'profile': profile, 'profile_sha256': sha(args.profile),
               'image_id': args.image_id, 'jobs': args.jobs, 'status': 'started',
               'commands': [], 'boot_tested': False, 'glibc_tested': False}
    with (work / 'build.log').open('w') as log:
        def run(command, cwd=None):
            receipt['commands'].append(command)
            log.write('$ ' + repr(command) + '\n')
            log.flush()
            result = subprocess.run(command, cwd=cwd, stdout=log, stderr=subprocess.STDOUT,
                                    env={**os.environ, 'KBUILD_BUILD_USER': 'tabor',
                                         'KBUILD_BUILD_HOST': 'lab',
                                         'KBUILD_BUILD_TIMESTAMP': '1970-01-01 00:00:00 UTC',
                                         'KBUILD_BUILD_VERSION': '1'})
            if result.returncode:
                raise RuntimeError('Command failed: ' + repr(command))
        try:
            source = within(inputs, profile['source'])
            run(['git', '-C', str(source), 'cat-file', '-e', profile['commit'] + '^{commit}'])
            for item in profile['patches'] + [profile['config']] + profile.get('copies', []):
                p = within(inputs, item['path'])
                if sha(p) != item['sha256']:
                    raise ValueError('Input hash mismatch: ' + item['path'])
            checkout = work / 'source'
            checkout.mkdir()
            # Archive committed bytes, never copy a dirty checkout or share mutable inodes.
            archive = work / 'source.tar'
            run(['git', '-C', str(source), 'archive', '--format=tar',
                 '--output=' + str(archive), profile['commit']])
            with tarfile.open(archive) as t:
                t.extractall(checkout, filter='data')
            archive.unlink()
            for item in profile['patches']:
                patch = str(within(inputs, item['path']))
                run(['git', 'apply', '--check', patch], cwd=checkout)
                run(['git', 'apply', patch], cwd=checkout)
            for item in profile.get('copies', []):
                target = within(checkout, item['destination'])
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(within(inputs, item['path']).read_bytes())
            output = work / 'output'
            output.mkdir()
            (output / '.config').write_bytes(within(inputs, profile['config']['path']).read_bytes())
            receipt['status'] = 'prepared'
            if not args.prepare_only:
                cc = profile['cross_compile']
                run([cc + 'gcc', '--version'])
                run([cc + 'ld', '--version'])
                run(['dpkg-query', '-W'])
                make = ['make', '-C', str(checkout), 'O=' + str(output),
                        'ARCH=' + profile['arch'], 'CROSS_COMPILE=' + cc]
                run(make + ['olddefconfig'])
                config = (output / '.config').read_text().splitlines()
                for key, value in profile.get('required_config', {}).items():
                    if key + '=' + value not in config:
                        raise ValueError('Required config missing after olddefconfig: ' + key)
                run(make + ['-j' + str(args.jobs)] + profile['targets'])
                receipt['status'] = 'compiled'
            receipt['final_config_sha256'] = sha(output / '.config')
            receipt['output_sha256'] = {str(p.relative_to(output)): sha(p)
                                       for p in output.rglob('*') if p.is_file()}
        except Exception as exc:
            receipt['status'] = 'failed'
            receipt['error'] = str(exc)
            raise
        finally:
            (work / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'] + ': ' + str(work / 'receipt.json'))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--profile', type=Path, required=True)
    p.add_argument('--inputs', type=Path, required=True)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--jobs', type=int, default=2)
    p.add_argument('--image-id', required=True)
    p.add_argument('--prepare-only', action='store_true')
    try:
        execute(p.parse_args())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
