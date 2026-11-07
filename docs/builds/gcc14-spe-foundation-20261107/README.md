# Fresh Trixie SPE foundation qualification — 2026-11-07

User directs a fresh userspace rebuild with newer GCC. Candidate profile:
profiles/trixie-spe-sdk-candidate.json. Selected modern target is frozen Trixie
GCC14.2.0-19 and patched glibc2.41-12+deb13u4, Linux powerpc-linux-gnuspe,
PPC32 big-endian SPE GPR double/128-bit long double. This is not an AmigaOS ABI.

All three GCC14 Debian source files already existed in the server cache and
match their locked SHA256/size. No network fetch. Fresh dpkg-source extraction
passed in a4CPU/6GiB/network-none container. Actual upstream source archive
inside the Debian wrapper is gcc-14.2.0-dfsg.tar.xz. The newlib archive also in
that wrapper is not the selected Linux libc. Preserve Debian patch/packaging
semantics when preparing the upstream compiler build.

The original GNU GCC8.5 archive SHA512 matches the retained official pin.
Inventoried162 files under its dedicated powerpcspe backend/runtime paths.
These are restoration reference material, not an accepted GCC14 patch set.
No legacy SDK/compiler root or consumer package was replaced.

## Actual modern-compiler gate

Ordinary Debian PowerPC GCC14.2.0-19 rejects all three required flags:
-mabi=spe, -mspe and -mfloat-gprs=double. probe.c also requires __SPE__ and emits
a double addition. Probe returns1; no accepted SPE object is produced. This is
an expected negative qualification, not a working compiler or fresh userspace.

## Bounded next implementation

Expand the locked upstream archive in a fresh server work directory and compare
GCC8 powerpcspe config selection, target hooks, machine descriptions and libgcc
save/restore/unwind support against GCC14 interfaces. Prepare component patches
with regression purposes; importing old files alone does not establish support.
First acceptance is modern compiler generation of the selected SPE ABI and
compatible libgcc. Then use normal Debian bootstrap mechanisms for patched
glibc, finish compiler C/C++ runtime and run the full ABI/fenv/unwind gates.
Build genuine foundation packages, qualify clean sbuild roots and rebuild the
selected workstation closure only after those producer gates pass.

Use a known-working QEMU kernel for compiler/runtime comparisons; the clean7.3
experiment's secondary-CPU stall is a separate pre-userspace issue. Do not
restart an old-GCC package batch and call it a modern rebuild, or assume a new
compiler alone fixes fenv. Keep the staged USB candidate inactive for now.
