# Core blocker hand-walk — 2026-11-11

Audit in run018 completed normal sbuild exit0 and payload inspection with Debian's
supported cross,nocheck,nopython profile. Target installation is not yet tested.

Reviewed concrete compiler failures:

- xxhash: raw make install reverted to native cc and attempted to link SPE
  objects with the native linker. Use dh_auto_install with target /usr paths;
  debhelper supplies cross tools and DESTDIR. New patch/spec registered.
- grep: Debian warning patch declares immediately after stray_backslash label;
  the existing tracked pre-C23 compatibility patch was not wired to the current
  registry. Registered a quilt source spec using that existing series.
- ncurses: existing tracked patch recognizes linux-gnuspe in GNU/Linux glibc
  feature selection. It too lacked active registry wiring. Registered its quilt
  source spec; preserve implicit-declaration diagnostics.

Actual run-sbuild-package prepare_only checks pass all three in
work/handwalk-source-check-20261111-024. This includes actual patch application
and dpkg-source repackaging, not compilation. Superseded queued snapshots
019–023 were stopped before package builds; retained for provenance.
Run024 is queued after018 with the reviewed inputs and normal four-job bounds.
Compilation and subsequent apt/dpkg root installation remain acceptance gates.

Final orchestration check:018 stopped after accepted audit because five new
producer names were absent from image-builder packages inventory despite their
registered source paths. Added cunit/jansson/libseccomp/libva/tpm2-tss to that
inventory.025 starts directly with corrected inventory and all reviewed fixes,
reusing accepted audit.024 never reached package compilation.
