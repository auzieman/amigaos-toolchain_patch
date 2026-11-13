# Debian builder comparison and corrective inputs — 2026-11-11

References reviewed:
- https://wiki.debian.org/SupportedArchitectures
- https://wiki.debian.org/CrossCompiling
- https://manpages.debian.org/trixie/debhelper/dh_auto_install.1.en.html

POWER8/9 Debian ppc64el is a maintained 64-bit LE ABI; powerpcspe is a retired
32-bit BE/SPE ABI. Its packages and compiler are not substitutes. The maintained
port is a workflow reference, not evidence that all sources cross-build unchanged.

Our failure classes must remain distinct: source/compiler compatibility,
missing target producer packages, supported bootstrap profiles, architecture
registration, and orchestration errors. Existing sbuild host/build architecture
and apt dependency handling remain the standard mechanisms; no replacement solver.

Corrective work for026:
- Actual libseccomp Debian control/rules honor nopython. Register it in the
  bootstrap stage with full bindings rebuild retained; removes target Python
  dependency from the C library bootstrap used by apt.
- xxhash dh_auto_install does not itself supply target CC for this makefile.
  Pass DEB_HOST_GNU_TYPE-gcc and -ar explicitly, preserving normal DESTDIR.
- submit-port-build now checks selected sources against builder inventory and
  registered source locks before any remote submission. This catches the exact
  missing-inventory error from018 locally instead of after accepted builds.

026 submitted with existing 4x4CPU/6GiB package bounds, frozen sources and SDK.
No GCC14 promotion, new target ABI or base refresh. Compile/install/runtime
qualification remains pending; do not call the whole build service fixed yet.
