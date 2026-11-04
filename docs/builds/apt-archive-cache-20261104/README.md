# Persistent apt archives

Source intake already checks and reuses pinned archives. The missing cache was
apt's binary downloads inside disposable sbuild roots. In addition to losing
those roots, sbuild defaults `APT_KEEP_DOWNLOADED_PACKAGES` to false, overriding
the template's retention policy during dependency installation.

The runner now uses documented `unshare_bind_mounts` and
`apt_keep_downloaded_packages`, disables apt clean/distclean, and retains
archives outside build roots at `/srv/data1/tabor-apt-cache`. Each worker has
its own apt lock and partial directory. Complete `.deb` files are hard-linked
from/to a shared pool under a short exchange lock; partial files never enter
the pool. Retained failed/interrupted workers are scanned before new workers
start. Hard links avoid multiplying payload storage. Apt remains responsible
for authenticating indexes and validating requested package hashes. Frozen
versions, dependency resolution and installed state are unchanged.

The cache was seeded with 1,155 existing archives. The retained native offline
check re-requested `libbrotli1=1.1.0-2+deb13u1` with nspawn private networking
and a read-only root: exit0, `Need to get 0 B/304 kB`. Warnings concerned attempts
to chmod the deliberately read-only apt list directory; acquisition succeeded.
The fixture performs download-only, not package installation or target code
execution. `scripts/check-apt-archive-cache.py` repeats this check with explicit
paths. Receipt: [offline-receipt.json](offline-receipt.json).

Round `port-pipeline-20261104-006` includes this correction. Its first full
sbuild bind-mount/acquisition result is still pending; the native offline check
does not establish target build, image or runtime acceptance. Uncached files
still require the frozen archive to respond; retries are retained.
