# Constrained Debian/SPE package cycle

Run from this project on the workstation:

```sh
python3 scripts/submit-debian-package.py --package libmd --iteration 006
```

Use a fresh iteration number. This command checks for an active package build,
synchronizes the reviewed recipe/lock/patch files, and submits one network-free
R730 Docker job (4 CPU equivalents,6GiB,256 tasks). It does not compile locally,
launch extra viewers, retry unknown failures or overwrite accepted artifacts.
The whitelist expands after source/dependency/recipe review, not arbitrary shell
commands. Image digest, sysroot and compiler paths are pinned in
profiles/images/debian-package-builder.json; native image package inventory is
/opt/tabor-package-host-packages.txt. Image builds record their actual digest;
Dockerfile apt resolution is not independently snapshot-locked.

The runner verifies cached sources, freshly extracts Debian source, applies
version/hash-checked ordered patches, then invokes normal dpkg-buildpackage and
debian/rules. Build-dependency checking stays enabled. Native debhelper produces
control data, shlibs/symbols, triggers and any maintainer scripts. Target tests
are deferred using the standard cross/nocheck profile, not run on x86.
Recorded SPE flags and restored glibc2.41 sysroot select the same experimental
ABI used by our existing Mesa/EFL diagnostics; existing Mesa is source-built,
not evidence that all graphics packages need or contain a patch. Never use
native x86 libraries to satisfy target linkage.

Libmd's bootstrap cross-packaging patch explicitly supplies the recorded target
libc search path and a shlibs mapping. That mapping is not a claim that libc6
is already installed; it generates a real libc6 dependency that must be met by
our eventual target libc package. Unset TABOR_SYSROOT leaves ordinary source
packaging unchanged. Gzip transport supports the initial target dpkg; udeb's
normal xz/extreme defaults require explicitly resetting compression strategy to
none when choosing gzip. Reference:
https://manpages.debian.org/trixie/dpkg/dpkg-deb.1.en.html .

Logs, success/failure receipts, .deb/.udeb, .changes and .buildinfo stay under
/srv/data1/tabor-build/linux-live-001/work/debian-PACKAGE-ITERATION. New source
fixes go into patches/PACKAGE with origins and hashes before the next attempt.
There is no automatic compiler-error patch invention or forced dependency install.

## Current acceptance

Libmd1.1.0-2+tabor1 packages built, including normal symbols/shlibs/triggers.
The packaged-build library passes target MD5/SHA256 known vectors. Full target
installation does not pass: root lacks a real libc6 package record and GNU tar.
Target dpkg-deb fails on BusyBox tar's unsupported --warning=no-timestamp.
Restore the Debian Essential package set (including implicit dependencies), not
just explicit package Depends. GNU tar and real libc/bootstrap packages precede
normal installation; do not force these dependencies or treat extraction as
configuration. Then progress through libbsd/PAM/udev/logind/session closure.
The single-user goal still permits normal Debian system accounts and services.

Directed-rounding/fenv, complete Debian desktop setup, E compositor rendering
and physical Radeon output remain independent open gates. No USB write.
