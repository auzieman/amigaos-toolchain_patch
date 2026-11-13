# Workstation blocker recheck — 2026-11-11

Read-only R730 recheck after its reboot: 128810 MiB RAM, 127173 MiB available,
load 0.04; no loaded tabor systemd jobs. No builds restarted or target changed.

## Foundation

`work/gcc14-sdk-20261108-001/qualification-002.json` remains
`failed-not-promoted`, despite SDK build exit 0. Its retained
`probe-compile-002.log` fails the C++ link with undefined virtual and non-virtual
thunks to `std::strstream::~strstream()`. GCC14 is not an accepted workstation
SDK. Preserve the frozen foundation; do not substitute vanilla glibc for the
required patched SPE source specification.

## Build root and libraries

Latest retained package controller is `port-pipeline-20261104-022`.
Its fallout has 28 unique source names: one foundation source-spec gate,
two package installation failures (zlib and krb5), 25 dependency-blocked sources.
Repeated zlib entries across stages are one source, not independent defects.

The concrete installation failure in
`port-pipeline-20261104-022-base-libraries-zlib/sbuild.log` is:

```
error creating symbolic link './usr/lib/tabor-spe-toolchain/powerpc-linux-gnuspe/lib/libatomic.a': Read-only file system
```

This is build-root/package-layout infrastructure, before source compilation;
not evidence zlib or Kerberos source needs fixing. Resolve the package-owned
path versus read-only SDK mount contract before retrying the same batch.

Dependency chains reported by the retained Debian solver include Python3.13
headers blocked by Bluetooth development headers; BlueZ needs D-Bus development
packages; D-Bus/systemd/PAM/Xorg/OpenSSH need audit development packages; audit,
curl and libtirpc need Kerberos development packages. HarfBuzz needs the GIR
build helper and Mesa needs sensors development packages. These are retained
solver results, not a new solver evaluation or proof of full closure.

## Applications

EFL awaits curl development packages, Enlightenment awaits connman development
packages, and Terminology awaits EFL. Xorg awaits audit. No fresh package batch,
complete package-managed desktop root, or application acceptance is claimed.
Keep GPU acceleration work separate from the software desktop path.

Next: correct and qualify the SDK mount/package install boundary with the
representative zlib build, then rerun Debian dependency checks. GCC14 C++ ABI
qualification is a separate foundation blocker, not a reason to retry blocked
applications unchanged.

## Packaging correction started

`prepare-libatomic-packaging.py` now generates canonical revision tabor2 with
only the normal target linker symlink. Both SDK-directory links were removed;
the provider package revision is unchanged. An isolated corrected source package
was prepared from the retained canonical003 source and submitted to standard
sbuild on R730 as `tabor-libatomic-boundary-20261111`, limited to4 CPUs/6GiB.
Evidence: `work/libatomic-sdk-boundary-20261111-001/` (source, command, build log,
result exit). No pool promotion or zlib consumer retry until payload acceptance.

The isolated libatomic tabor2 sbuild completed successfully (exit0,49seconds).
This establishes package construction, not installation into the shared-SDK
consumer root; payload inspection and zlib retry remain pending.
See [incremental validation](incremental-validation.md) for the QEMU/USB CLI
checkpoint scaffold, separate from GPU rendering acceptance.

## Proactive workstation dependency restart

User explicitly requests complete release-related development provisioning and
target dependency builds, including PAM, OpenSSL, OpenSSH, Bash, GTK and X11.
The corrected libatomic runtime/development pair passed payload/ELF inspection;
all sbuild specs referencing the old canonical dev receipt now pin that pair.
The old build-root-only atomic provider is removed from those specs so its
version1 cannot conflict with development package version2's exact dependency.
Master SDK remains read-only.

Submitted `port-boundary-20261111-001` via the normal pipeline for zlib acceptance
using the corrected inputs. This is an infrastructure gate, not the broad
package batch. Prepared `profiles/sbuild/workstation-dependencies-20261111.json`
for the subsequent batch, explicitly including Bash/OpenSSL in addition to the
existing PAM/OpenSSH/X11 list. GTK3/GTK4 were missing from the selected source
inventory; bounded authenticated frozen-source intake/cache is running as
`tabor-workstation-intake-20261111`. Integrate verified source locks and evaluate
its complete Debian dependency closure before claiming GTK is queued/built.
No broad batch has been launched yet; no claim that all development dependencies
are cached or built. GCC14 remains an independent qualification failure.

### Follow-up: stale build-essential dependency

First zlib retry was solver-blocked: crossbuild-essential spe5 still required
old tabor-spe-libatomic1 exactly. Removing its provider without updating this
adapter was an integration omission, not a zlib compiler failure. Built and
payload-inspected spe6 metapackage depending on canonical libatomic1 tabor2
and tabor-spe-libatomic-dev tabor2. Updated sbuild receipt pins/core version and
submitted port-boundary-20261111-002. No consumer pass yet. GTK3/GTK4 archive
cache completed:3.24.49-3 and4.18.6+ds-2, respectively.

### Cross-chroot coinstallation correction

Round002 exposed canonical libatomic1 Multi-Arch:same version conflict with
native GCC14's libatomic1 inside the disposable chroot (not physical-host
package mutation). Restored the separately named, versioned-Provides bootstrap
runtime. Canonical tabor3 development package permits libatomic1>=tabor1,
retains target-only files, and is selected alongside the existing real provider.
Metapackage spe7 pins that provider plus development tabor3. Both rebuilt and
payload-inspected. No package metadata fabricated or force-overwrite used.
Submitted broader port-workstation-20261111-003 with Debian dependency gates;
GTK3/GTK4 source locks/cache added to selected builder inputs. This remains
bootstrap GCC8; GCC14 SDK is separately unqualified. Submission is not proof
of accepted compilation or target runtime.

### Stop shared wrapper faults before scaling

Round003 failed before invoking sbuild: wrapper hard-coded core versions through
spe5, rejecting spe7. Replaced that allowlist with dpkg version validation and
an exact match against the verified build-essential .deb in the extra inputs.
New batch-controller code classifies absence of any sbuild log as pre-sbuild
setup failure and halts after the current wave rather than feeding the same
wrapper failure through additional consumers/stages. Syntax checks pass; actual
foundation qualification submitted as port-foundation-20261111-004. These new
controller guards apply to later frozen submissions, not an edited live run.

### zlib source packaging diagnosis

Foundation004 completed dependency installation and cross-compiled zlib itself.
Bundled contrib/minizip configure omitted --host/--build and CC, selected native
gcc, reported cross compiling=no, and linked amd64 objects against SPE libz.
Native ld rejected the incompatible libz files. Registered a hashed packaging
patch passing explicit Debian build/host tuples and target CC/AR to that nested
configure. No global gcc override or SDK mutation. Queued isolated
port-zlib-cross-20261111-006 behind workstation005; independent work continues.
Patch application/build acceptance pending. Prior generic source-build category
does not imply a defect in zlib's C implementation.

### Broad fall-through007 submitted

Compared early build-desktop-base.py: explicit SPE CC environment and upstream
zlib configure/make/install; it did not exercise Debian contrib/minizip. This
is narrower than an accepted standard source-package build. Existing managed
builder explicitly removed CC for Debian tuple-aware rules, so a universal
restoration of absolute CC would regress OpenSSL prefix handling. Retain the
narrow nested-configure patch instead.

New plan workstation-fallthrough-20261111.json includes180 unique selected
sources with verified local source-lock entries,84 bootstrap candidates,
4 concurrent ready jobs. Includes the existing builder's full selected package
inventory, beyond the prior shorter workstation queue. Deferred unrelated
scope/compiler candidates stay excluded. Replaced waiting zlib-only006 with
port-fallthrough-20261111-007 behind workstation005; no active workers killed.
007 frozen submission includes corrected libatomic/metapackage receipts and
zlib patch plus wrapper early-failure guard. Dependency readiness and isolated
build fallout still use normal Debian tools. No180-source completion claimed.

### Post-laptop-space recheck: shared mount exhaustion

007 stopped correctly on pre-sbuild setup failure. Five source packages passed:
attr,dash,libsepol,pcre2,base-files. gzip/debianutils encountered bind mount
ENOSPC. Server storage has1.3TiB free on data1 and1TiB on root. mountinfo shows
32767 stacked entries at the exact SDK path (32797 total; mount-max100000).
Shared SDK helper used os.path.ismount, which misses same-filesystem bind mounts,
so repeated calls could create additional stacked shared mounts. Replaced that
check with exact /proc/self/mountinfo mountpoint/options detection. Syntax passes;
cleanup of stacked mounts and live acceptance pending. No reboot/SDK mutation.
This is separate from laptop VLC log exhaustion.

PNY checksum dry-run completed exit0:271484 entries,69844316996 bytes, zero
created/deleted/transferred files. No PNY formatting performed by this recheck.

## Continuous pipeline foundation repair

Controller now prepares/verifies the shared SDK once before source dispatch;
workers only require exactly one read-only mount and never mount/remount it.
Duplicate mounts stop startup explicitly. The SDK/master and archive caches
remain persistent; source build roots remain disposable. Same-filesystem bind
mount detection reads exact mountinfo entries rather than os.path.ismount.

Four focused regression tests pass: same-filesystem bind detection, repeated
preparation without mounting, duplicate rejection without mutation, and worker
rejection of missing/writable mounts without mutation. Shell-independent Python
syntax validation passes. Isolated R730 unshare test of recursive overmount
cleanup passed before applying cleanup to the exact SDK path.

Controlled cleanup unit tabor-foundation-repair-20261111 verifies inactive
controllers and absence of nested mounts, removes only stacked SDK mounts,
rehashes the existing SDK on remount, and requires one read-only mount after
ten repeated preparation calls. Evidence is retained under
work/pipeline-foundation-repair-20261111-001. No broad build is launched until
that receipt passes and actual sbuild acceptance is recorded.

Controlled cleanup completed successfully:32767 mounts reduced to1, SDK content
verified, ten repeated preparation checks retained exactly1 read-only mount.
No files deleted. Submitted port-qualification-20261111-008: force four small
known-buildable sources (attr,dash,libsepol,pcre2) through normal Debian clean
sbuild roots with4-worker limits. Not a full archive rebuild. Source preparation
now filters registry entries to selected sources instead of preparing unrelated
patch specs on every run. Broad queue remains held pending this qualification.

### Restore verified dependency providers

Audit rejected prior zlib same-version binary outputs solely for differing
new source-patch hash. This removed actual zlib1g-dev providers and blocked
Python despite existing packages. Earlier zlib504 and libcap-ng503 outputs now
pass standalone hash/ELF inspection (6 and5 package entries respectively).
Changed audit to retain same-source-version dependency providers regardless of
new patch selection; worker build reuse still requires exact patch evidence.
libcap-ng uses upstream-supported nopython bootstrap with full rebuild retained.
Queued provider recheck011 behind009 with standard preflight and source-fallout
continuation. Submission010 used the qualification-only clean-predecessor gate
inappropriately and was stopped/replaced; no successful build claimed for it.
Remaining dependency resolution must be observed, not assumed resolved.

Zlib follow-up diagnosis: miniunzip's final target link reports libz.so.1 needed
by libminizip.so not found. Prepared build-only -Wl,-rpath-link=$(CURDIR) for
nested minizip configure alongside target CC/AR/build/host selection. No runtime
RPATH added. Registered patch hash updated locally; frozen009/011 unchanged.
Build validation pending; no additional queue restart submitted for this edit.
