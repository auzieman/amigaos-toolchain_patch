# Debian bootstrap libraries — 2026-11-01

Three fresh, normal Debian package builds with corrected SPE compiler
(gcc-unwind-003 / native package8.5.0+tabor2). One4CPU/6GiB server build at a
time, then1CPU/1GiB probe jobs. No local compilation or new viewers.

| Source | Binary version | Artifacts (includes debug/installer outputs) | Runtime |
| --- | --- | --- | --- |
| libcap-ng | 0.8.5-4+tabor1 | 5 | QEMU library smoke PASS |
| libsepol | 3.8.1-1+tabor1 | 4 | QEMU library smoke PASS |
| pcre2 | 10.46-1~deb13u3+tabor1 | 7 | QEMU library smoke PASS |

libcap-ng uses Debian's supported nopython bootstrap profile; full Python
bindings are deferred, not removed from the source. libsepol preserves
Debian hardening flags while appending explicit SPE ABI flags. PCRE2 preserves
Debian regex symbol-prefix flags and existing disabled JIT for powerpcspe.
Packages retain standard Debian maintainer metadata, symbols/shlibs, triggers
and permissions. This does not mean they are configured in the target root.

## Verified target tests

Probe libraries match actual .deb payload hashes. Compiled against package
headers and libraries, then uploaded and read back to verify hashes. Loader
maps confirm these libraries and private packaged libc004 in existing system
QEMU. See qemu-tests.json, per-package probe build receipts and raw logs.

- libcap-ng: process capability query, clear local library state, reload and
  compare. No capng_apply, privilege change or host capability mutation.
- libsepol: allocate and free policy database. Not policy enforcement testing.
- PCRE2: ASCII match, expected nonmatch and Unicode-letter UTF-8 match; JIT=0.

The initial cap-ng001 build compiled but dependency generation could not
identify /sysroot/lib/ld.so.1. Added shlibs mapping to its actual libc6 owner;
normal checks remain enabled. Fresh002 passes. Failure receipt/tail retained.
The mapping expresses a real required libc6 package, not a fake installed
record. No manual target dpkg status entries or suppressed maintainer scripts.

Patch series, source locks, image, compiler frontend identity, source/recipe
hashes and package hashes are retained. Upstream license/copyright metadata
stays in generated Debian packages; license-review.json records inspected
packaging copyright hashes/labels for the first two libraries. Source intake
uses pinned HTTPS DSC/payload SHA256; independent OpenPGP chain remains pending.

## Remaining gates

Continue libselinux (now sepol/PCRE prerequisites built), audit (cap-ng built),
libcap2 and their genuine development-package dependencies, then full-feature
libc and GNU tar/Essential closure. A cross-build sysroot is an input, not an
installed Debian image: final target package configuration, maintainer scripts,
triggers and service state still need running and persistent-root verification.
Do not mark build dependencies satisfied with dummy records. Keep known fenv
rounding #3, E compositor #8 and physical A1222/Radeon acceptance separate.
No new graphical root/noVNC candidate, drive write or installed-runtime change.
