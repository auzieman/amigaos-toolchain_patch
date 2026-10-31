# Review starting point

Private working repository for Auzieman and invited collaborators. Current
implementation targets Linux/SPE on A1222/Tabor; AmigaOS SDK integration still
needs its host/target/runtime contract. The repository name does not establish
that Linux glibc can serve as an AmigaOS C runtime.

Start with the [engineering progress log](progress.md) for commit/run context.
The [matched Mandelbrot demo](../bench/README.md) includes ASCII timings,
identical fractal images and a side-by-side graphic with explicit QEMU limits.

The [minimal image package plan](minimal-package-plan.md) records the requested
8 GiB/Radeon target, staged E/GL payload and optional browser, without claiming
a completed target dependency solution or image.

Current Linux increment: [R730 rescue-image workflow](r730-live-image.md),
with [native SSH/CLI evidence](builds/r730-live-20261031/results-ascii.txt).
The VM132-inspired desktop remains a subsequent source-built increment.

## Prompts and workflows

- [.agents/prompts](../.agents/prompts): intake, baseline kernel, kernel
  forward-port and SPE forward-port task starters.
- [.agents/skills](../.agents/skills): corresponding source/build/ABI workflows.
- [Patch plan](patch-set-plan.md), [Debian iterations](debian-iterations.md),
  [source inventory](vendor-source-intake.md).

## Actual patch status

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
