# POWER8-compatible ppc64el xxhash control — 2026-11-11

User requested a simple previously failing package on the maintained POWER8 ABI.
Actual clean frozen Debian sbuild/unshare amd64→ppc64el comparison, source
xxhash0.8.3-2, normal Debian GCC14 crossbuild-essential/apt dependency resolution.
No SPE compiler, SDK mount, target packages or dependency overrides were used.

- work/power8-xxhash-control-20261111-001: unmodified Debian source FAILED,
  exit2, after7seconds build/72seconds total. override_dh_auto_install invoked
  native ld on PowerPC64 objects (EM21), identical failure class to SPE EM20.
- work/power8-xxhash-control-20261111-002: same source plus registered xxhash
  install fix (explicit target CC/AR through dh_auto_install), PASSED exit0,
  45seconds total, five ppc64el debs. Actual xxhsum ELF inspected: ELF64,
  little endian, PowerPC64. Source preparation/DSC and output hashes retained.

This establishes a cross-build packaging failure independent of SPE, and
qualifies the fix on ppc64el. It does not assert native POWER8 builds fail,
physical POWER8 execution, SPE acceptance or a complete build-service fix.
The port controller/batch dispatch was temporarily stopped during each control
to preserve total concurrency limits and resumed in finally handlers.
