"""Restore the verified compiler's read-only mount after a server reboot."""
import fcntl,subprocess,hashlib
from pathlib import Path


def exact_mounts(path):
    # ismount() cannot reliably identify same-filesystem bind mounts.
    # Read the exact mountpoint, not findmnt --target's containing filesystem.
    target=str(Path(path).resolve())
    matches=[line.split()[5].split(',') for line in Path('/proc/self/mountinfo').read_text().splitlines()
             if line.split()[4]==target]
    return matches


def require_read_only(path):
    mounts=exact_mounts(path)
    assert len(mounts)==1, 'Shared SDK must have exactly one mount; run foundation preparation, not a package retry'
    assert 'ro' in mounts[0], 'Shared SDK must be read-only'


def ensure_read_only(path, manifest):
    path=Path(path)
    with (path.parents[2]/'.mount.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        mounts=exact_mounts(path)
        assert len(mounts)<=1, 'Duplicate SDK mounts require controlled cleanup before builds'
        options=mounts[0] if mounts else None
        if options is not None and 'ro' in options:return
        for name,expected in manifest.items():
            file=path/name
            assert file.resolve().is_relative_to(path.resolve()) and not file.is_symlink()
            with file.open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==expected
        if options is None:subprocess.run(['mount','--bind',str(path),str(path)],check=True)
        subprocess.run(['mount','-o','remount,bind,ro',str(path)],check=True)
        require_read_only(path)
