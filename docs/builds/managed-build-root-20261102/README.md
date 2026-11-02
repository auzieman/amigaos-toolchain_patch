# Package-managed cross-build root transition

Current verified result: fresh pkgconf403 builds/packages without a consumer
patch; all five managed-foundation sources (attr, libxcrypt, fribidi, pixman,
mtdev) pass. ELF payload inspection confirms their packaged CPU objects are
ELF32 big-endian PowerPC. Real attr runtime/dev installation then unblocks
ACL401 compilation and packaging. No target runtime tests ran in these builds.


The broad source checks expose a shared foundation problem: target libraries
were compiled and archived, but the corresponding development packages are not
installed in the effective build root. A copied header/library tree cannot
satisfy Debian's Build-Depends checks. The existing dpkg-cross bootstrap packages
provide real transport metadata but do not by themselves establish the ordinary
architecture-qualified development package state required by those checks.

The next step uses apt/dpkg in an isolated native container to install the real
powerpcspe library/header packages. Native host tools remain native; there is
one source-build target, powerpcspe. No native counterpart source rebuild or
emulator registration is introduced. This follows Debian's documented
[cross dependency model](https://wiki.debian.org/Multiarch/CrossDependencies)
and [cross-building workflow](https://wiki.debian.org/CrossCompiling).

## Version and provenance policy

Debian's Multi-Arch:same library coinstallation requires matching versions and
matching common payload files. Our automatic +tabor1 changelog/version rewrite
prevents that even when source versions otherwise match. The new explicit
preserve_debian_version recipe option leaves the pinned upstream changelog and
version unchanged; source/archive/patch/compiler hashes and build profiles
continue to be recorded in the build receipt. This does not rewrite an existing
.deb, native package record, dependency or installed version.

Fresh glibc401 uses the existing six SPE patches, corrected GCC8.5+tabor3 and
pinned 2.41-12+deb13u4 sources, matching installed native Debian binaries. It is
still a stage2/nobiarch bootstrap build. Its preserved-version artifacts are
build-root bootstrap inputs only and must not be promoted as full-feature libc
or silently replace the separately versioned target-archive artifacts. A normal
feature rebuild remains required once audit/capability/SELinux dependencies are
available. Original immutable compiler/sysroot inputs remain untouched.

The package_managed_root mode sets the compiler sysroot to the container root
and omits TABOR_SYSROOT/TABOR_SHLIBS bootstrap transport overrides. Dependency
checks and dpkg-buildpackage remain enabled. Actual package installation and
configuration are performed by apt/dpkg in the target-development Docker recipe,
not by extraction plus synthetic status records. Final A1222 root installation,
boot and runtime acceptance are still separate gates.

## pkgconf dependency

Read-only inspection of the installed Debian metadata establishes:

- pkgconf1.8.1-4 is architecture-specific, Multi-Arch:same, with cross scripts.
- pkgconf-bin1.8.1-4 is Multi-Arch:foreign and supplies the native executable.
- Sources from the Debian archive are cached/hash-pinned in
  profiles/build-dependency-sources.lock.json. No prior local cached pkgconf
  archive was found in the bounded search across the build area's cache roots.

Building the source for powerpcspe and installing only its pkgconf script
package can satisfy target-qualified script dependencies while retaining the
installed native pkgconf-bin. Target binaries emitted by that source are kept
separate and are not executed. Source copyright inspection records ISC and BSD-4 notices, preserved unchanged.
Actual package payload/build acceptance remains pending. Source DSC/file hash
checks are not independent OpenPGP trust-chain verification.

Current work is on R730, one heavy job at a time,4CPUs/6GiB. No new viewer,
QEMU session, USB write or final target installation is implied by this work.

## Verified libc installation and exposed UAPI gap

Libc401 completed seven packages. The first two installation attempts exposed
apt's --no-download handling of local .deb paths (relative and absolute). The
third removed that option while keeping Docker networking disabled. Apt/dpkg
then installed/configured libc6 and libc6-dev:powerpcspe normally, processed
native triggers and passed an empty dpkg audit. Exact hashes, context and logs
are retained; no package metadata was forced or rewritten.

The first pkgconf build in that root reaches real compilation, then fails on
`asm/errno.h`: ordinary libc headers resolve, but the standard Debian universal
linux-libc-dev package lacks a gnuspe tuple symlink farm. This is an observed
missing header registration, not an SPE instruction or runtime failure.

Source patch0002 adds the gnuspe tuple to Debian's existing UAPI symlink rule.
It is an alternative to the old target-only header packaging patch0001, not an
additional patch after0001. The new explicit debian-all-uapi export keeps the
normal Architecture:all package metadata and complete data payload. It invokes
only the header-export/packaging target, never a kernel build or another target
code compilation. Debian's universal header package inherently contains
architecture-independent data for multiple include tuples; native build tools
and this target share that ordinary package. No other executable build target
is introduced. Fresh Linux-header401 validates this source-level correction.

The target-development recipe requires the canonical gnuspe UAPI path. It supplies
explicit, hash-checked local inputs so the universal data package receives its
patched payload through normal apt installation. This retains
normal maintainer scripts and dpkg ownership rather than copying aliases into
the container by hand. No target ELF execution is required by this stage.

## The next producer defect: libc linker-script format

The normal universal UAPI package built and installed. Ownership/path validation
and a clean audit are retained in uapi-installed-state.json. Pkgconf402 then
compiles successfully, but shared linking rejects libc's installed development
script. Libc401's script says OUTPUT_FORMAT(elf32-big), while the copied older
sysroot says elf32-powerpc. Configuration records OBJDUMP='objdump'. The retained
comparison on the same freshly compiled PPC object proves native objdump emits
elf32-big/UNKNOWN and cross objdump emits elf32-powerpc/powerpc:common.

Ordered glibc patch0007 selects the actual cross objdump in the SPE architecture
file. Fresh libc402 uses all seven hash-pinned patches; configuration now records
OBJDUMP='powerpc-linux-gnuspe-objdump'. No installed script or generated .deb is
rewritten. Issues12 and13 track the UAPI and libc-producer failures separately;
acceptance requires installation and a fresh successful pkgconf package build.
The current header/libc build scripts' exact input recipes are retained here
with their receipt hashes; future manual submissions freeze per-iteration
snapshots and verify their file hashes before building, like the serial queue.

A new libc output gate in the runner rejects an incorrect packaged linker-script
format. This additional gate was added after libc402 started; its result must
therefore be recorded separately for that run, not claimed as part of its
original recipe. Bootstrap libc artifacts still cannot be promoted as a final
runtime merely because dpkg configuration succeeds.

Installation recipe evolution: UAPI image001 inherited old local .deb files and
--reinstall attempted unavailable native coinstallation siblings. Image002
cleared only the task-owned input directory and installed normally, then
reinstalled the reviewed Arch:all data. Its first normal apt installation
already unpacked the new same-version header payload. The current recipe omits
the redundant reinstall loop and verifies the canonical header path and audit;
the next package layer exercises that simplified recipe.

## Subsequent queue

Once corrected libc and pkgconf scripts are installed, the reviewed foundation
queue attempts attr, libxcrypt, fribidi, pixman and mtdev sequentially. Each runs
Debian dependency preflight before compilation. Failures are retained while
independent sources continue. Actual development package installation and ACL
retry follow after reviewing the attr artifacts. The queue is not a replacement
for Debian's dependency solver and does not promote artifacts automatically.

## Shared SDK correction and completed source gates

The deeper objdump cause is SDK layout: bootstrap supplied prefixed aliases in
bin/ but omitted the TARGET/bin directory GCC's own program lookup searches.
The staged native SDK8.5.0+tabor4 adds nine links to the installed real PowerPC
binutils. Original compiler inputs remain untouched; hashes and dependencies
are recorded in sdk-layout-receipt.json. All nine GCC -print-prog-name lookups
resolve to the cross tools (sdk-binutils-lookup.json). This common correction
benefits all consumers; no additional library-specific patch is needed.

The explicit glibc objdump selection remains a deterministic bootstrap fallback.
Retire it only after a fresh libc build without that fallback passes using the
fixed SDK (preferably the required normal-feature libc rebuild). No such removal
or new full-feature runtime acceptance is claimed here.

Corrected libc402 plus header401 install normally in a fresh root. Pkgconf403
then passes source compilation and Debian packaging, with no bootstrap shlibs
mapping, no leaked SDK paths and no target ELF in its script/personality package.
That target package installs while pkgconf-bin remains native. Five queued
foundation sources subsequently pass and their actual packages, not just files,
feed the next root update. ACL401 builds after real attr runtime/dev installation,
closing the originally demonstrated ACL dependency-state failure.

The common package-builder profile now uses the configured managed root for
ordinary sources; source-specific old image/prefix overrides are removed. The
stage2 libc bootstrap remains an explicit exception. Managed submissions do not
mount the old /tools or /sysroot trees, preventing silent fallback to copied
inputs. Source/patch/cache selection and normal Debian profiles remain intact.
Manual recipes have per-iteration snapshots; the serial queue freezes metadata
inputs and retains failed attempts while building independent ready sources.

Archive010's old libc6-dev is confirmed to contain the same incorrect BFD format.
The next manifest explicitly excludes that known-defective development artifact,
records its hash/reason, and leaves immutable old archives intact. The corrected
preserved-version stage2 libc remains build-root-only. A final accepted target
archive needs a properly versioned full-feature replacement; selected dependency
simulation passing is not a substitute for actual linking/configuration.

## Verified checkpoint and current shared blocker

Corrected libc402, universal headers401 and genuine target development packages
install through apt/dpkg with clean audit. Seven ordinary sources pass normal
Debian packaging: pkgconf403, attr401, libxcrypt401, fribidi401, pixman401,
mtdev401 and ACL401. Subsequent libmd501 and libcap-ng501 also pass.
The remaining65 queue reports 65 dependency blocks, not 65 compiler failures.
Its scope is the original working group, not complete desktop dependency closure.

Libsepol501 and PCRE2-501 expose a shared compiler installation defect: their
normal Debian rules replace injected CFLAGS, revealing the SDK default /sysroot
rather than the configured development root /. These are not evidence that each
consumer needs a source patch. Issue14 tracks a fresh GCC8.5 source rebuild with
--with-sysroot=/ and separate --with-build-sysroot=/sysroot. Standard TARGET/bin
binutils lookup links are now also created by the compiler bootstrap helper.
The helper adds default-root/default-ABI checks and an assembly-only SPE probe.

At this checkpoint tabor-gcc-system-root-001 is running on R730, limited to
4 CPUs/6 GiB. Inputs are frozen under submissions/gcc-system-root-001/project;
work and output are fresh gcc-system-root-001 directories. Native build image:
sha256:2781e11839beffa351f8c411d71b7e2bd1ae0336d24c60b407778c3350dd9da0.
The existing runtime bootstrap sysroot remains read-only. The rebuild and new
post-build checks have NOT yet passed; installation and fresh consumer retries
remain required. This is still GCC8 bootstrap work, not modern GCC restoration.

Signed archive011 contains 83 artifacts, explicitly quarantining the old
incorrect libc6-dev. Signature/update/policy checks pass; dependency simulations
remain blocked without a suitable final development runtime and full closure.
Preserved-version stage2 libc is restricted to build-root use. No new accepted
target root, graphical boot, hardware validation or USB write is claimed.
