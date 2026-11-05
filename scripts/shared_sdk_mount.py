"""Restore the verified compiler's read-only mount after a server reboot."""
import fcntl,os,subprocess,hashlib
from pathlib import Path


def ensure_read_only(path, manifest):
    path=Path(path)
    with (path.parents[2]/'.mount.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        options=subprocess.check_output(['findmnt','--noheadings','--output','VFS-OPTIONS','--target',path],text=True).strip().split(',')
        if os.path.ismount(path) and 'ro' in options:return
        for name,expected in manifest.items():
            file=path/name
            assert file.resolve().is_relative_to(path.resolve()) and not file.is_symlink()
            with file.open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==expected
        if not os.path.ismount(path):subprocess.run(['mount','--bind',str(path),str(path)],check=True)
        subprocess.run(['mount','-o','remount,bind,ro',str(path)],check=True)
        assert 'ro' in subprocess.check_output(['findmnt','--noheadings','--output','VFS-OPTIONS','--target',path],text=True).strip().split(',')
