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
