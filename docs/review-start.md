# Review starting point

Current package workflow: [Debian port skill](../.agents/skills/tabor-debian-port/SKILL.md)
and [R730 broad dependency provisioning/source intake](builds/port-build-server-20261102/README.md).
Provisioning is running; this is not new-image acceptance. See progress.md for
the latest verified results rather than interpreting older running queues below
as current worker status.

Private working repository for Auzieman and invited collaborators. Current
implementation targets Linux/SPE on A1222/Tabor; AmigaOS SDK integration still
needs its host/target/runtime contract. The repository name does not establish
that Linux glibc can serve as an AmigaOS C runtime.

Current direction: [Debian workflow audit](debian-workflow-audit-20261102.md)
replaces custom dependency management with a standard sbuild/apt proof. The
cumulative-root results remain bootstrap evidence.

Previous checkpoint: ncurses/zstd/LZ4 and image/font development packages pass
build/normal cross-root installation. The remaining70-source core queue is
running; a fresh desktop image still needs complete target package setup.
See [acceptance evidence](builds/sdk-defaults-20261102/README.md).

Start with the [engineering progress log](progress.md) for commit/run context.
The [matched Mandelbrot demo](../bench/README.md) includes ASCII timings,
identical fractal images and a side-by-side graphic with explicit QEMU limits.

The [minimal image package plan](minimal-package-plan.md) records the requested
8 GiB/Radeon target, staged E/GL payload and optional browser, without claiming
a completed target dependency solution or image.

Earlier Linux increment: [R730 rescue-image workflow](r730-live-image.md),
with [native SSH/CLI evidence](builds/r730-live-20261031/results-ascii.txt).
The VM132-inspired desktop remains a subsequent source-built increment.

The [desktop foundation checkpoint](desktop-foundation.md) now includes tested
shared C++ execution and exact EFL/E/Terminology source seeds.

## Prompts and workflows

- [.agents/prompts](../.agents/prompts): intake, baseline kernel, kernel
  forward-port and SPE forward-port task starters.
- [.agents/skills](../.agents/skills): corresponding source/build/ABI workflows.
- [Patch plan](patch-set-plan.md), [Debian iterations](debian-iterations.md),
  [source inventory](vendor-source-intake.md).

## Current status — 2026-11-02

The active [managed build-root transition](builds/managed-build-root-20261102/README.md)
replaces copied target development files with real apt/dpkg installation and
Debian dependency checks. Patched libc6/libc6-dev coinstallation and UAPI header
ownership have passed; nine subsequent ordinary source builds pass. The next
compiler default-sysroot defect (issue14) is fixed: installed SDK5 C/C++
checks and fresh libsepol/PCRE2 packaging pass. See
[compiler-default evidence](builds/sdk-defaults-20261102/README.md). Native build
tools are installed. The first20-source dependency wave passes15; xz then
passes in normal architecture-only mode. Genuine installed runtime providers
and GMP development packages close the host/target runtime-identity gap in
the isolated cross-build root. Further dependency waves remain in progress. JPEG/GPM/PCI/font registration
retries pass; selected artifacts pass static payload inspection and development
packages install normally. LZ4 builds and installs; ncurses GNU/SPE feature-test registration is under
fresh verification (issue18), followed by zstd with its prerequisites installed. This is an isolated cross-build root, not a configured target
installation or new graphical boot.

Corrected GCC8.5 SPE PIC/C++ unwinding and selected glibc runtime tests have
passed in QEMU; see [libc/compiler evidence](builds/glibc-debian-20261101/007-runtime-result.md).
The source-level restoration/packaging series now has seven patches. Directed
rounding remains issue3; full-feature libc, full ABI acceptance and modern GCC
backend restoration remain separate gates. GCC8 is the current bootstrap
compiler, not a claim of restored GCC14 support.

Signed archive010 contains64 artifacts; GMP301 packaging passes. The73-source
readiness group is working scope, not proof of dependency closure. No accepted
normally configured Trixie desktop root exists yet. E black client interiors
(issue8), target-root integration (issue7), packaged runtime acceptance (issue11),
UAPI registration (issue12), libc tool selection (issue13), and physical board
acceptance remain separately tracked until their actual gates pass.

## Initial investigation — 2026-10-30

- patches/linux/0001-powerpc-tabor-initial-machine-dts.patch: initial modern
  Tabor machine and vendor-derived DTS, applied in the current kernel experiment.
  Audio, DIU, reset/power control and boot wrapping remain separate work.
- patches/glibc/0001-restore-historical-e500-sysdeps.patch: preparatory recovery
  of 36 deleted e500-only files. Configure rejection and shared state handlers
  remain unchanged. This is not functional SPE/glibc enablement.
- patches/gcc and patches/binutils: no accepted restoration patches yet.

Targets: Debian linux 6.12.113-1 and glibc 2.41-12+deb13u4. Source pins, patch
origins and checks are recorded. The full modern Tabor vmlinux/modules/dtbs
cross-compile passed in BKC run b57b3f7b-cc3c-43b4-95a7-31b11186478b;
returned hashes verified. See [full build evidence](builds/20261030-full-debian-kernel.json).
The glibc patch applied, then Debian GCC rejected SPE flags: no restored libc
ABI is claimed. A separate minimal QEMU configuration booted with two e500v2 CPUs and reached
freestanding PPC32 init;
see [emulator recipe and limits](qemu-boot.md). Actual A1222 boot remains pending.
Selected single/double SPE arithmetic also passed in a later init test; see
[direct SPE and minimal graphics status](minimal-e-gears.md). This does not
validate the full SPE ABI or modern libc.
Earlier infrastructure/configuration failures remain in docs/task.md.
The proposed [E-Trixie image follow-up](e-trixie-follow-up.md) records the
remaining compiler/ABI, rescue rootfs, real-board and graphics gates.

Seven local tests pass, including source isolation, independent patch replay,
cache rejection and refusal to reuse a run directory. Fixture tests do not
substitute for real Debian extraction, cross-compilation or hardware tests.

Cached archives/vendor checkouts, generated source/object trees, private media,
SDK payloads and lab build artifacts are excluded from Git. Patches retain
upstream notices and do not relicense third-party source. Lab submission scripts
refer to Auzieman's BKC environment; collaborators can inspect/reuse the generic
runner with their own Docker mounts without those lab credentials.


2026-10-31 software-session checkpoint: EFL/E/Terminology target builds now
complete and a separate filesystem boots into E's standard profile via target
Xvfb/VNC. This is partial graphical acceptance: shelf/icons/frames render, but
client interiors are black (issue8). Locale/keyboard and optional service work
is issue7; directed rounding remains issue3. See software-e-session.md and
builds/r730-software-session-20261031 for exact receipts, screenshot and retained
failures. Physical A1222/Radeon/OpenGL remain untested by this checkpoint.


Package/hardware increment: package-hardware-readiness.md records private
installed SPE deb bundles and native dpkg, corrected helper permissions/system
bus, qemu-live007 with8GiB and two online CPUs, pinned-core arithmetic/page tests,
and actual physical-kernel SMP/MMU/HIGHMEM/SPE/DMA configuration. These are
emulator/configuration gates only; physical8GiB/CPU startup and GL/Radeon are
still pending. Black client interiors persist with SysV shared-memory segments
attached in software-e007; issue8 stays open. Exact board revision remains to
verify despite the user-reported age/A1222 Plus reference. Evidence is under
builds/r730-packaged-session-20261031. No USB writes occurred.


2026-11-02 desktop build-service handoff: preserve the compiler/ABI research and
verified bootstrap packages. Further desktop closure uses a fresh native
mmdebstrap buildd root and Debian sbuild/unshare with apt resolution, accumulating
artifacts rather than permanent root mutations. See debian-workflow-audit-20261102.md.
The first versioned universal UAPI source/profile build is in progress; a clean
SPE libxdmcp cross-build proof follows. No new desktop/boot acceptance yet.
