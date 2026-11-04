# Scripted Debian port build cycle

Submit the reviewed recipe, rather than launching builds package by package:

```sh
python3 scripts/submit-port-build.py \
  --run-id port-pipeline-20261103-001 \
  --native-audit work/debian-dependency-audit-009
```

Each run ID must be new. The submitter refuses overlapping package controllers,
freezes source/patch/profile inputs remotely and starts one bounded R730
controller. Heavy work stays on the server. Existing native Debian binaries
supply native tools; the target remains powerpcspe.

The controller prepares reviewed source changes with dpkg-source first.
Dependency checks read those actual prepared DSCs, so a Build-Depends fix is
visible before any build is scheduled. Original inputs, patch hashes and
prepared-source receipts remain linked. This corrects the earlier standalone
libtool attempt that supplied too narrow an extra-package set and missed SPE
zlib. The pipeline uses Debian's installation set instead.

Debian dose-builddebcheck evaluates architecture/profile-qualified requirements;
sbuild/apt installs their genuine packages in disposable roots. The package
inventory is not a replacement solver. Up to four ready package jobs use the
completed native dependency template and disk-backed temporary roots, each
bounded to4 CPUs/6GiB. Successful artifacts accumulate in the pool. Ready sets
are recalculated after each wave; unrelated failures do not stop ready work.

The first stage builds the reviewed base-library prerequisites. util-linux
uses its existing stage1/pkg.util-linux.noverity profiles for bootstrap, then
must receive the required full rebuild. db5.3 uses its existing notcl profile
because the selected image needs its C library, not its Tcl binding package.
The second stage schedules the selected desktop/services and required normal
rebuilds. Unqualified vanilla foundation sources are not substitutes for the
accepted SPE restoration; required patched-source specs remain explicit gates.

Fixes belong in profiles/port-package-overrides.json and version/hash-pinned
source patches/specs. Supported profiles and packaging changes are passed to
both the solver and builder. Record omitted outputs; rebuild them if a selected
final binary needs them. No fabricated installed state, path overrides or
suppressed maintainer scripts are part of this cycle.

Each run retains receipt.json, prepared-sources.json, stage plans/logs and
fallout.json. Failure summaries distinguish dependency installation, source,
packaging and infrastructure errors while preserving raw logs. Accepted builds
are reused only when source/profile/patch evidence matches. Failed input
fingerprints prevent an unchanged failure being retried across stages; a
reviewed change or new dependency installation set permits another attempt.
The script reports gaps for evaluation; it does not guess source fixes.

Missing producer intake is separately bounded by an explicit reviewed source
list. plan-port-dependency-intake.py --only-producers uses the actual audited
failure report, including bootstrap profiles, then the existing authenticated
source-cache tool verifies archives against the frozen indexes. It can chain
archive caching with --cache and --cache-output. Metadata discovery never
authorizes building every language runtime, web server or compiler encountered.

Native helper correction: dh-golang1.63 initialized cross-Go state while
debhelper was merely discovering backends for C sources. The packaged fix moves
that setup to the documented pre_building_step hook. Four native regression
checks reproduce the original failure, accept patched C/SPE discovery, retain
the explicit unsupported-Go/SPE failure and preserve native Go setup. Popt and
Tcl-defaults subsequently pass standard cross packaging with that helper.

This pipeline builds packages. Target apt/dpkg configuration, QEMU session
painting, GL/SPE demos and physical A1222 tests remain separate gates; a green
package stage alone does not authorize or establish a completed boot image.

A reviewed follow-up may use --after-run PREVIOUS_RUN_ID. It waits remotely
for normal predecessor completion, refuses overlapping workers and stops if
the predecessor has an infrastructure failure. Submitted inputs stay frozen.

Pool indexing reads actual .deb Source/Version fields and excludes obsolete
variants outside the selected source version, with explicit foundation
exceptions. Historical artifacts remain retained; package metadata is never
rewritten to force coinstallation.

Shared SDK/header acceptance precedes consumer patches. Revision tabor6 repairs
GCC8-generated quoted Linux header probes at SDK staging time. Current sbuild
inputs pin SDK6/core5 explicitly; the original immutable base lock and native
root receipts are retained. See patches/gcc/bootstrap-8.5/README-fixed-headers.md.

The controller imports fingerprinted failures from completed prior rounds.
An unchanged input set is deferred; changed SDK, source/profile or solver
installation inputs permit a new attempt. This avoids repeatedly compiling
the same known failure merely because a new run ID was selected.

Bootstrap/profile choices use original Debian control/rules, not assumptions
based on source names. References:
https://wiki.debian.org/CrossCompiling
https://wiki.debian.org/DebianBootstrap
https://wiki.debian.org/BuildProfileSpec
