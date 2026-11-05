"""Publish verified job inputs as an immutable flat apt repository for sbuild.

Dependency/version selection remains apt's job. This only avoids sbuild copying
hundreds of --extra-package files through its namespace one file at a time.
"""
import fcntl
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def prepare(extras, parent):
    extras, parent = Path(extras), Path(parent)
    files = sorted(extras.glob('*.deb'))
    assert files and all(not p.is_symlink() for p in files)
    inputs = {p.name: digest(p) for p in files}
    identity = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()
    parent.mkdir(exist_ok=True)
    assert not parent.is_symlink()
    parent.chmod(0o755)
    destination = parent / identity
    with (parent / '.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if destination.exists():
            record = json.loads((destination / 'receipt.json').read_text())
            assert record['inputs'] == inputs
            assert digest(destination / 'Packages') == record['packages_sha256']
            assert all(digest(destination / name) == sha for name, sha in inputs.items())
            return destination, record
        staging = Path(tempfile.mkdtemp(prefix='.staging-', dir=parent))
        try:
            for source in files:
                # Copies here are outside user namespaces, once per archive
                # content set; keep originals' modes and ownership untouched.
                shutil.copyfile(source, staging / source.name)
                assert digest(staging / source.name) == inputs[source.name]
                (staging / source.name).chmod(0o444)
            with (staging / 'Packages').open('wb') as output:
                subprocess.run(['dpkg-scanpackages', '--multiversion', '.', '/dev/null'],
                               cwd=staging, stdout=output, stderr=subprocess.PIPE, check=True)
            record = {'inputs': inputs, 'packages_sha256': digest(staging / 'Packages'),
                      'identity': identity, 'method': 'dpkg-scanpackages --multiversion; standard apt flat repository'}
            (staging / 'receipt.json').write_text(json.dumps(record, indent=2) + '\n')
            for name in ['Packages', 'receipt.json']:
                (staging / name).chmod(0o444)
            staging.chmod(0o555)
            os.rename(staging, destination)
        finally:
            if staging.exists():
                staging.chmod(0o755)
                shutil.rmtree(staging)
    return destination, record
