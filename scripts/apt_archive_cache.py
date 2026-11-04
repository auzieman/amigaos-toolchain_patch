"""Persistent apt archives; apt still owns acquisition and hash validation.

Each sbuild gets its own writable bind mount/lock/partial directory. Complete
archives are linked into a shared pool under a short lock, never partial files.
A failed or interrupted build's retained archives seed subsequent workers too.
"""
import fcntl
import os
from pathlib import Path


def exchange(pool, directories):
    count = 0
    for directory in directories:
        for archive in directory.glob('*.deb'):
            if archive.is_symlink() or not archive.is_file():
                continue
            try:
                os.link(archive, pool / archive.name)
                count += 1
            except FileExistsError:
                pass  # apt validates the requested archive against signed metadata.
    return count


def prepare(cache_base, job, seed, uid, gid):
    cache_base = Path(cache_base)
    cache_base.mkdir(exist_ok=True, mode=0o755)
    pool = cache_base / 'pool'
    workers = cache_base / 'workers'
    pool.mkdir(exist_ok=True)
    workers.mkdir(exist_ok=True)
    worker = workers / job
    worker.mkdir(exist_ok=False)
    os.chown(worker, uid, gid)
    with (cache_base / 'exchange.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        exchange(pool, [Path(seed), *workers.iterdir()])
        exchange(worker, [pool])
    return worker


def retain(cache_base, worker):
    cache_base = Path(cache_base)
    with (cache_base / 'exchange.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        added = exchange(cache_base / 'pool', [Path(worker)])
    return {'path': str(worker), 'promoted_archives': added,
            'retained_archives': len(list(Path(worker).glob('*.deb')))}
