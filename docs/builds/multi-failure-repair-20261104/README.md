# Whole-fallout repair — 2026-11-04

Reviewed all actual failed builds and the deferred chains from round017.
That round produced12 inspected source builds /66 debs, including systemd's
bootstrap libraries, DRM, coreutils, base-passwd and cdebconf. Raw fallout is
history across phases: Tk's earlier acquisition failure was followed by a
successful normal build. Do not present every retained phase failure as an
independent current compiler defect. round017-results.json retains acceptance
receipt and payload-inspection hashes.

## Failure matrix and shared repairs

| Observed failure / chain | Shared cause | Concrete repair / qualification |
| --- | --- | --- |
| Kerberos byacc fetch503/504 despite verified bytes in pool | Debian pool filenames omit epochs; apt cache names include encoded epoch | Preserve source-named files and create checksum-verified canonical apt names. Actual sbuild-usernsexec --nonet failed before / passed after,126kB requested versus0B. |
| Tk x11proto-core-dev fetch; Kerberos byacc alternative | dose and apt can select different valid alternatives; prefetch is a prediction | On primary install-deps acquisition failure, map actual requested URLs to frozen native index, fill exact hashes, refresh worker cache and retry once. Preserve first log. Never classify compiler/coinstallation failures as downloads. |
| BLT dependencies unavailable although dose previously reported ready | Our wrapper exposed only one dose-selected SPE installation set | Expose the entire verified SPE archive through sbuild's normal extra-package repository. Apt owns its own actual resolution; packages are available, not universally preinstalled. |
| BLT Native Tk/SPE Tk library coinstallation | Multi-Arch:same requires exact binary versions across both architectures | Review full actual Tk helper closure: Xft+b4, Xext+b3, Xss+b3. All three rebuilt successfully in018 with six inspected debs. |
| Repeated version conflicts across core libraries | Existing reviewed requests in image-builder metadata were ignored by the standard registry path | Reconcile14 previously missing entries; verify all16 old requests against frozen native metadata and selected source versions. Add a fail-fast consistency check and select outstanding core requests in019. This is not automatic version inference or a base upgrade. |
| Python defaults blocked on target Sphinx | Documentation generators execute on build host but lacked native qualifiers | Patch both control and control.in with :native for docutils/Sphinx/html2text, retaining normal outputs. Real source apply/repack/DSC preparation qualified before full batch. |
| Xaw/Mesa/Avahi missing development libraries | Remaining target producers | Hash-verify/register libxpm, libxxf86vm and libdaemon together from signed frozen metadata. |

Remaining GIR/introspection, full restored-glibc source packaging, full-feature
bootstrap follow-through, target installation and QEMU/physical gates stay
explicit. No new boot image or GPU/runtime acceptance is implied.

## Evidence and boundaries

* epoch-before.json and epoch-after.json: same frozen native root, actual sbuild
  UID/GID mappings, bind mount and networking disabled. The cached byacc file
  was invisible under its pool filename; the verified encoded-epoch alias
  changed acquisition from126kB to0B. No package installation/target code ran.
* epoch-alias-receipt.json: original verified files reused; no re-download.
* recovery-real-logs.json: actual Tk and Kerberos log requests matched exact
  frozen native files; the actual BLT coinstallation failure did not trigger
  acquisition recovery.
* Nine regression tests passed on R730: five recovery/cache-refresh boundary
  tests, four native cache tests including epoch-name reuse without network.
  Synthetic fixtures are not archive-authentication evidence.
* python-source-proof.json: actual prepared DSC for native tool qualifiers;
  source version preserved and normal packaging retained. Initial zero-context
  draft was rejected in qualification001; contextual patch passed002.
* tk-coinstall-review.json: full native Tk library-chain mismatches, rather
  than the first reported Xft conflict alone.
* existing-revision-review.json: all16 previously reviewed core binary revision
  requests match the authenticated frozen native versions. The old image
  profile remains checked against the standard registry to prevent silent drift.

Round018 runs the combined infrastructure/metadata fixes and already passed
Xft/Xext/Xss rebuilds. Round019 is explicitly queued after018, reusing successful
outputs and addressing outstanding pre-existing core binary revisions with
max4 dependency-ready 4-CPU/6GiB jobs. It adds no new target architecture and
does not overlap package workers. Debian dose/apt/sbuild retain dependency,
installation, profile and maintainer-script semantics.


Follow-up qualification: round018 has accepted six sources /13 inspected
binaries: Xft, Xext, Xss, Xpm, Xaw and libdaemon. This is not a desktop or
10–20 completed-source claim. Review of all three actual source failures found:

* Python Docutils is Architecture:all, Multi-Arch:foreign. Adding :native was
  incorrect: installed Dpkg::Deps::KnownFacts explicitly rejects that
  combination. Restore its unqualified dependency in control and template;
  keep native qualifiers for Sphinx/html2text. The real archive metadata and
  standard dpkg evaluator reproduce rejected-before/accepted-after semantics.
* BLT's Debian gcc-15.patch unconditionally changed ANYARGS to C23 unnamed
  variadics. Retain the Debian patch, but guard that syntax for C++/C23.
  Actual pinned GCC8 rejects the old declaration and accepts the corrected one.
  This is a source/compiler-version compatibility issue, not missing SPE code.
* libxxf86vm's malloc(0) configure test needs the already measured Xorg cache
  answer; include it in the existing reviewed consumer set. No new ABI guess.

Both corrected source packages apply/repack successfully on R730 with original
Debian versions preserved (followup-source-003-*). Full source build acceptance
remains pending. Active018 was not interrupted. Waiting-only019 was cancelled
before any builds, original receipt retained, and replaced by020 after018 with
these corrections plus all previous reviewed core binary rebuilds. No worker
overlap, no baseline change. Full-archive sbuild staging is currently visible
setup overhead; copying archive files is not counted as compilation progress.
