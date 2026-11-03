# Standard Debian builder proof — 2026-11-02

The research/bootstrap artifacts remain valid. Desktop dependency closure now
uses mmdebstrap buildd roots, unprivileged sbuild/unshare and normal apt resolution.
See [workflow audit](../../debian-workflow-audit-20261102.md).

* Native root: R730 work/debian-buildd-root-001, receipt native-buildd-root.json.
* Accepted headers: work/sbuild-linux-uapi-007, receipt linux-uapi007.json.
  Debian Linux6.12.113-1 plus SPE UAPI tuple registration, proper source revision
  6.12.113-1+spe1, standard header-only profiles. Normal .changes/.buildinfo and
  Architecture:all package retained remotely; static package inspection passes.
* Next proof: work/sbuild-libxdmcp-005, build=amd64/host=powerpcspe.
  Standard apt must select the genuine compiler/bootstrap library packages;
  no target execution or image acceptance is implied.

Headers attempts004–006 retained failures in local source preparation, then007
passed without bypassing Debian checks. Earlier Docker proof failures are
infrastructure evidence, not source-port failures. The earlier bootstrap
compiler/libc/runtime inputs remain explicitly intermediate. Full-feature libc,
complete desktop dependencies, target configuration and QEMU/physical runtime
acceptance remain open.

Libxdmcp004 was given back before compilation: missing target pkgconf and an
incorrectly host-qualified universal-header core dependency. Libxdmcp005 adds
the real pkgconf403 script/personality package (native pkgconf-bin executes)
and explicitly selects linux-libc-dev:native, legitimate for its Architecture:all
Multi-Arch:foreign data. Build-Depends remain enabled and unchanged.

## Frozen baseline (latest user direction)

Use profiles/trixie-spe-base.lock.json: Linux6.12.115-2, glibc2.41-12+deb13u4,
SDK8.5.0+tabor5 and snapshot20261102T220000Z. Do not refresh versions during
iterations. Earlier results above retain their original pins; they do not
establish acceptance of the selected new source revision.

Frozen-root001 correctly failed its exact-version gate because the midnight
snapshot still contained6.12.113-1. Frozen-root002 uses the fixed22:00 snapshot
(the security Release is dated21:33 UTC), retaining the same selected versions.
The snapshot selection is part of establishing this baseline, not an automatic
upgrade loop. Linux-UAPI008 was rejected before building because the old root
lacked the new base-lock identity. No checks were bypassed.

Frozen-root002 now passes: native linux-libc-dev6.12.115-2 and libc6
2.41-12+deb13u4 exactly match the lock. frozen-buildd-root.json and
frozen-installed-versions.json retain root/manifest hashes and all native
package versions. UAPI009 now rebuilds the SPE tuple patch from source6.12.115-2
in that frozen standard root. Add its accepted receipt to the libxdmcp input
set only after packaging and static inspection pass; no accepted009 result yet.

## Current fixed-path acceptance

UAPI009 passes: linux-libc-dev6.12.115-2+spe1, normal Debian source/header-only
profiles, package/static-inspection hashes in linux-uapi009.json. Libxdmcp006
then passes unpatched source1:1.1.5-1 with real dependencies resolved/installed
by apt in frozen root002. It produces libxdmcp6 and libxdmcp-dev SPE packages,
normal .changes/.buildinfo and static payload verification (libxdmcp006.json).
Documentation olink warnings were nonfatal; sbuild and inspection passed.
These current results supersede the earlier blockers for these exact slices.
They do not claim target runtime or a newly assembled desktop image yet.
Libxcb001 now runs through the same standard path. The viewport summary has
been updated from its stale legacy queue failure summary.

Libxcb001 also passes standard sbuild packaging and payload inspection, with its
receipt retained as libxcb001.json. The serial X11 sequence starts libx11 next,
then eleven remaining selected X11 libraries. scripts/run-sbuild-sequence.py is
only a serial dispatcher: each source still uses sbuild/apt in a fresh frozen
root; accepted output artifacts enter subsequent standard extra-package inputs.
It does not decide dependency closure, bypass failures or assemble a target root.
The R730 service is tabor-sbuild-sequence, output work/sbuild-x11-sequence-001;
resource ceiling is4 CPUs/6GiB and the existing live summary shows this queue.
The QEMU-after-new-image request remains pending accepted image assembly; no
old diagnostic image is relabeled as this fixed build.

2026-11-02 follow-up: the first12-source X11 pass finished with libX11's configure
runtime-test refusal and11 dependent missing-libx11-dev blocks. Reusing the
existing measured SPE malloc-zero cache through sbuild's BUILD_ENVIRONMENT
fixes that prerequisite; libx11-002 passes normal packaging. The prior queue
was badly ordered after its prerequisite failed. Next dispatch uses Debian's
dose-builddebcheck against authenticated frozen native Packages and actual SPE
binary controls, with build=amd64/host=powerpcspe and cross,nocheck profiles.
Native tools and target development packages install through apt before any
source compilation; target execution remains a separate QEMU stage.

## Dependency-ready parallel queue

Evidence: libx11002.json, cross-core-metapackage001.json, dependency-audit005.json
and dependency-summary005.json. The full native/target dependency installation
sets and failure chains are under R730 work/debian-dependency-audit-005.
The real port metapackage is a native source-built Architecture:all dependency
entry point; it provides no false compiler/runtime identities. Its dependency
installation passes in the first4 new roots.

R730 work/ready-sbuild-batch-002 is the current controller, selecting only
Debian dose-ready sources from the49 remaining reviewed groups. It runs4
isolated sbuild jobs at most,4 CPUs/6GiB each, then refreshes the Debian solver
report with newly accepted artifacts. Build dependencies install normally before
compilation; target code is not executed. The viewport tracks live queue state.
Batch001 and its stop-note.json retain the obsolete-libc pool error; no checks
were disabled to accept that mixed pool. Batch002 pins libc402 and supplies only
artifacts named by the solver's installation sets.

The full reviewed scope is108 source groups, not12 X11 libraries. Inventory at
this transition has59 source groups with successful receipts and245 distinct
.deb names across bootstrap work; these are not all rebuilt through sbuild or
configured on the target. Audit005 has66 ready/42 blocked source dependency sets.
These counts describe different gates and must not be added together.

## Broad desktop coverage and exact input selection

The user's control-center/Firefox suggestion is recorded as coverage probes:
work/wide-desktop-dependency-probes-002 and wide-desktop-relations-002. Authenticated
Sources metadata from the same frozen snapshot selects gnome-control-center and
firefox-esr; neither becomes an image selection or application build automatically.
Their whole-source dependency checks are blocked. Individual declared relation
checks cover99 relations with69 blockers under cross,nocheck/arch-only semantics;
this is not69 new mandatory packages and does not replace combined coinstallability.
Original source metadata, versions and full dependency expressions remain remote;
wide-desktop-probes002.json, wide-desktop-dependencies002.json, wide-relations002.json
and wide-relation-coverage002.json retain the results here.

Probe001 failed in the native metadata parser on a compressed stream. Probe002
uses the supported pure Python parser and completes. Relation probe001 had an
empty optional-field comparison error;002 completes. These are tooling failures,
not failures to compile GNOME/Firefox (neither application was compiled).

Parallel batch002 finishes with16 accepted source builds. Of its4 deferred
attempts, dpkg/tar/OpenSSL failed apt candidate selection because name-only pool
filtering still admitted obsolete +tabor versions; Lua reached packaging but
lacked globally installed target C++ runtime libraries. They are not4 compiler
failures. The next controller selects exact package/version/architecture/file
identities from Debian's solution. Real cross-core metapackage1.0+spe2 adds the
actual SPE runtime provider dependencies; Lua then passes in batch003.

Batch003 uses the corrected exact input set for dpkg,tar,Lua and OpenSSL. The
OpenSSL patch source check exposed inaccurate original diff line positions under
quilt --fuzz=0; the patch is regenerated against the pinned source and passes
native patch --dry-run --fuzz=0. Its registered JSON digest is updated. A new
OpenSSL retry must verify normal quilt/source packaging and the documented GCC8
hardening limitation. Private SPE source patches preserve Debian binary versions
for native/target coinstallation; generated patched DSC hashes identify the
modified source. No architecture fields or installed package states are forged.

75 reviewed source groups have successful package receipts at the batch002
checkpoint, including earlier bootstrap builds. Full-feature libc/binding rebuilds,
33 remaining source groups and final target installation/runtime gates remain
separate. The kernel/glibc/compiler baseline and snapshot have not changed.

Batch003 follow-up: dpkg,tar and Lua all pass with exact solver-selected inputs
and real compiler runtime preinstallation. Their receipts are dpkg003.json,
tar003.json and lua003.json; dependency-audit006.json records the refreshed universe.
The normal quilt --fuzz=0 application and source-package generation pass for
OpenSSL retry004, which is currently in sbuild. The unsupported GCC8 mitigation
remains explicitly documented; full packaging/runtime is not accepted yet.

The broad probes'99 relation checks use original Build-Depends and
Build-Depends-Arch with Debian profile/architecture semantics. Data/doc-independent
requirements are outside this arch-only probe. Results use the pre-wave005 SPE
universe; they are a dated coverage checkpoint, not a claim that every listed
blocker still exists after later library builds. For whole-source readiness,
always regenerate the standard solver report against the current artifact set.
