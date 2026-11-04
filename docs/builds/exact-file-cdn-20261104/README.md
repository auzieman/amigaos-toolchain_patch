# Exact-file CDN cache transport

R730 comparison of the same pinned bytes:

| File | Snapshot | snapshot-cloudflare | Debian CDN |
| --- | --- | --- | --- |
| autoconf-archive20220903-3 .deb |0.33s, hash verified (intermittent recovery after504s)|403|0.24s, same SHA256|
| json-c0.18+ds-1 DSC |18.14s timeout|403|0.07s, expected SHA256|

See comparison.json. This is a bounded two-file diagnosis, not a guarantee of
future CDN availability. Debian documents both /debian and /debian-security
on https://deb.debian.org/.

The cache tools now offer explicit --exact-file-cdn. Frozen signed Sources /
Packages metadata still selects exact names, versions, sizes and SHA256 values.
Only pinned Snapshot pool-file URIs can map to CDN pool-file URIs; suite/index
paths and unrelated origins are rejected. Source archives still require size
and SHA256 matches before cache promotion. Native archives use apt-helper with
the expected SHA256. Failed/missing/mismatched files do not select newer input.
Defaults remain Snapshot; the live mirror is not installed as an apt repository
or used for metadata/version selection. No base lock, apt source or root changed.
The explicit cache-only request avoids an automatic live-repository fallback.

Actual recovery: all4 closure source sets (json-c/keyutils/libevent/libtextwrap)
and libgcrypt20 completed size/hash verification. Their source locks are merged
in profiles/closure-prerequisite-sources.lock.json; normal source intake and
build registration consume them. Source-cache receipts retain the frozen index
and intake provenance. Native autoconf-archive was independently verified by
the comparison, and its archive is now retained (native cache run reused it).

Validation:3 transport tests cover exact filename mapping, security routing and
rejection of metadata/other origins;3 existing source-cache fault/reuse/integrity
tests still pass on R730. Real verified recovery is separate from those fixtures.

Round011 also passed AppArmor library bootstrap (2 debs) and GLib nogir build
(13 debs), with independent package payload inspection. Required AppArmor full
build, GIR and target runtime acceptance remain open. Round012 now includes
all5 recovered producers and is running; cached sources are not compiled results.
