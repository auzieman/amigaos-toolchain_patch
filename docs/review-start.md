# Review starting point

Private working repository for Auzieman and invited collaborators. Current
implementation targets Linux/SPE on A1222/Tabor; AmigaOS SDK integration still
needs its host/target/runtime contract. The repository name does not establish
that Linux glibc can serve as an AmigaOS C runtime.

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
origins and initial checks are recorded; no completed modern kernel compile,
restored libc ABI or real A1222 boot is claimed at this review checkpoint.
The first BKC attempt built its tools image but was stopped during slow NFS
extraction. The local-disk retry compiled Tabor board object and DTB; the full
kernel was interrupted to correct re-enabled debug information. The glibc patch
applied, then the Debian compiler rejected SPE flags. See
[actual iteration evidence](builds/20261030-first-debian-iteration.json). A fresh
full-kernel retry will use explicit DEBUG_INFO_NONE; docs/task.md retains failures.

Seven local tests pass, including source isolation, independent patch replay,
cache rejection and refusal to reuse a run directory. Fixture tests do not
substitute for real Debian extraction, cross-compilation or hardware tests.

Cached archives/vendor checkouts, generated source/object trees, private media,
SDK payloads and lab build artifacts are excluded from Git. Patches retain
upstream notices and do not relicense third-party source. Lab submission scripts
refer to Auzieman's BKC environment; collaborators can inspect/reuse the generic
runner with their own Docker mounts without those lab credentials.
