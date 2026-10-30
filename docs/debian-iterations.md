# Debian source iteration lane — 2026-10-30

Selected source packages: linux 6.12.113-1 (trixie security), glibc
2.41-12+deb13u4 (trixie). These are source baselines, not official Debian
powerpcspe binaries. Keep Linux's kernel compiler separate from the SPE
userspace compiler/runtime requirement.

Primary package references:
- https://packages.debian.org/source/trixie/linux
- https://packages.debian.org/source/trixie/glibc

## Immutable inputs, disposable work

`fetch-debian-sources.py` downloads missing files from the reviewed lock, checks
sizes/SHA256 and rejects changed cached files. Source DSCs were retrieved over
HTTPS; their recorded payload hashes are checked. Independent Debian archive
signature-chain verification is not yet implemented and is explicit in the lock.

`debian-iterate.py` refuses existing work directories, checks all cached inputs,
runs dpkg-source in a fresh location (applying Debian's source-package patches),
then applies our component series with git apply --check and git apply. Every
run records the lock, series and patch hashes; compiler/package versions; logs;
configuration and selected artifact hashes; and explicit failure/boot/ABI status.
Cache files are mounted read-only in the build container. The lab wrapper
retains receipts, configuration, scoped board artifacts, final kernel/modules
when available, then discards only that run's generated source/object directories. No changing a cached
source tree and pretending the next iteration started clean.

BKC template: pipeline/tabor-debian-iteration. Submission stages a content-hashed
bundle, registers only this pipeline and triggers it via the existing CLI/core.
An initial NFS extraction attempt was stopped for impractical metadata latency.
Fresh source/object trees now use a local per-run directory with an initial
4 GiB free-space requirement for kernel builds and a running 1 GiB free-space
stop guard. Completed outputs can be retained on shared storage; no reference
source is reused or edited.
The source bundle and logs remain under per-run /var/lib/bkc Tabor directories.
Runtime: 2 CPUs, 4 GiB, network disabled after image preparation. Result image
ID and its base digest are retained. Apt package versions are recorded; image
rebuilds are not snapshot-reproducible until that package set is also locked.

## Initial patches and limits

Linux 6.12 still has e500/SPE configuration. The initial Tabor patch adds a
modern machine-compatible binding and vendor-derived DTS with current relative
include paths. Shared P1022 initialization follows the modern upstream RDK
implementation (same SMP/PCI/SWIOTLB/MPIC sequence as the old vendor code).
Audio, DIU and board reset/power control are explicitly outside this first
serial/PCI compilation slice. No placeholder P1022DS identity is substituted
for the vendor Tabor DTS. Boot wrapper/real hardware tests remain separate.

The preparatory glibc patch restores 36 deleted-only e500 sysdeps files from
the upstream SPE removal's parent-side content. Exact origin/file list is in
glibc-restoration-origin.json. It leaves modern configure rejection and shared
state handlers unchanged; it is not a completed ABI port. The userspace build
preflight requires real SPE compiler flags, rather than silently compiling a
generic PowerPC libc. A rejection there identifies compiler restoration as a
prerequisite, not a successful glibc build.

## Verification

Seven local tests pass: source-isolation and safe artifact-retention tests plus archive-cache
rejection and fresh-run patch replay tests. The latter use a tiny extraction
fixture; only the lab job exercises actual Debian dpkg-source and compilation.
Per-run evidence, including failed experiments, is recorded in docs/task.md.
