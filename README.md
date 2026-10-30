# A1222 / SPE toolchain patches — private development

Start with [review status and prompts](docs/review-start.md).

Verified milestone (2026-10-30): the Debian 6.12.113-1 Tabor kernel completed
vmlinux/modules/dtbs cross-compilation. A separate minimal profile of the same
patched source booted on edge QEMU e500v2 with two CPUs and reached a static
PPC32 `/init`. See [boot evidence and recipe](docs/qemu-boot.md).
Selected SPE single/double additions also pass in a libc-free test; see
[minimal graphics and physical staging status](docs/minimal-e-gears.md).
Modern SPE/glibc ABI, physical A1222 boot and graphics remain unvalidated.
Proposed [E-Trixie live desktop follow-up](docs/e-trixie-follow-up.md) records
rescue rootfs, laptop appearance and SDL/GL testing goals.

Active patch objective: [restore missing e500v2/SPE support and forward-port
A-EON/Tabor changes](docs/patch-set-plan.md), with separate compiler, libc,
kernel CPU and board series and independently verified acceptance.

Current priority is A1222/Tabor and its e500v2 SPE support, which the user reports
Steven and Trevor asked them to investigate. Other A-EON platforms and the
user-described Marhi board belong to the longer-term scope; their exact hardware
identities and requirements remain to establish. Do not expand the current
patch/build slice to those boards. Keep reusable toolchain machinery separate
from board-specific profiles so later support can be added deliberately.

Build execution targets BKC lab-edge with constrained jobs; the R730 is optional
and not a dependency. The intended first hardware test is a minimal USB/rescue
image after kernel and boot-wrapper validation. Record its userspace ABI
explicitly; boot acceptance is separate from modern SPE/glibc acceptance.

Modernize the A1222/Tabor e500v2/SPE toolchain and Linux userspace, with a
separate future AmigaOS SDK integration track. Private collaboration repository:
https://github.com/auzieman/amigaos-toolchain_patch . No Hyperion source imported. Collaboration interest was reported by
the user; no access, endorsement or SDK compatibility is inferred.

## First deliverable

Reproduce the vendor Linux 5.4-rc3 baseline and boot format through the existing
`tabor-linux-forge` board workbench, then forward-port its small board/DTS/audio
series to a pinned modern kernel. A kernel build uses a freestanding PowerPC
compiler and binutils; it does not validate a target glibc or SPE userspace ABI.
Do not make a modern glibc a prerequisite for this first kernel artifact.

## Toolchain deliverable

Maintain separate versioned patch series for binutils, GCC/libgcc/libstdc++ and
glibc. GCC's SPE target was removed in GCC 9; glibc removed its SPE support in
2.30. Establish a historical SPE reference compiler/runtime first, then select
and pin the modern port target after auditing the removal and supplied patches.
A simple reverse-apply of the removal is an investigation aid, not an accepted
forward-port. Generic PowerPC soft-float and hard-float SPE are separate ABI
choices, not interchangeable compiler switches.

Bootstrap order: binutils → bootstrap GCC → Linux UAPI headers → libc bootstrap /
libgcc stages as required → complete glibc → final GCC/C++ runtime → ABI tests.
Record the exact bootstrap recipe and sysroot; host glibc and target glibc are
independent. Keep kernel-only compiler acceptance separate from userspace.

## Acceptance sequence

1. Vendor baseline patch/config/DTS provenance and unchanged build evidence.
2. Pinned modern kernel build, correct board DTB/boot wrapper, then serial boot
   on the A1222. QEMU e500 is useful but does not emulate the complete board.
3. Modern SPE compiler/runtime: ELF attributes and instructions; float/double,
   varargs, libm/fenv, setjmp/longjmp, signals/ucontext, pthread/TLS, atomics,
   exceptions/unwinding and C++ interoperability against a reference sysroot.
4. Linux graphics: kernel DRM/firmware plus userspace libdrm/Mesa/EGL/OpenGL
   built for the selected ABI. Software rendering and real GPU rendering are
   separate checks; GPU model and LLVM/JIT requirements remain to establish.
5. AmigaOS SDK: determine host/target, object/ABI/runtime requirements and supplied
   source/licenses. Linux glibc is not automatically an AmigaOS C runtime. No
   AmigaOS kernel build acceptance is possible before source/tool contracts exist.

See docs/feasibility.md, docs/intake.json and docs/task.md. Existing board source
remains owned by the separate Tabor workbench. This project stores references
and hashes, not a duplicate SDK, disk image or vendor code dump.

## Project workflows

Project-owned skills live under `.agents/skills/`:
`tabor-source-intake`, `tabor-kernel-build`, and `tabor-spe-forward-port`.
Reusable intake, baseline-build, kernel-forward-port and SPE-forward-port prompts
live in `.agents/prompts/`. These are discovered when working in this project;
no global agent configuration was changed.

The executable kernel path is documented in [kernel builds](docs/kernel-build.md):
`docker/Dockerfile.kernel` starts `scripts/kernel-build.py`, using the exact
vendor profile in `profiles/kernel-vendor-5.4-rc3.json`. The runner verifies
source revision and input hashes, exports committed source into fresh storage,
applies ordered patches and invokes configuration/build steps. It records
logs, compiler/package versions, configuration and output hashes, including a
failure receipt. It neither fetches nor patches GCC/glibc yet; their restoration
series remain empty until qualified source patches are available.

Validation: three real-Git fixture tests cover preparation/source isolation,
input-hash rejection, patch conflicts and refusal to reuse output storage.
All three skills pass the skill-creator validator. The tooling Docker image
and full vendor kernel have not yet been built with this new runner.

Deferred test environment: [Kyvos / AmigaOS provisioning](docs/future-amigaos-provisioning.md). This is separate from A1222/SPE validation and is not required for the current kernel baseline.

Manufacturer references: [Freescale/NXP P1022 source intake](docs/vendor-source-intake.md). Nine historical vendor repositories are now retained under ignored sources/vendor, pinned in profiles/vendor-sources.lock.json; this is not yet a complete SDK dependency closure.

## Debian iteration lane

The active modern targets are Debian trixie Linux **6.12.113-1** and glibc
**2.41-12+deb13u4**. `profiles/debian-trixie.lock.json` fixes source-package
filenames, origins and SHA256 values. Run `scripts/fetch-debian-sources.py` to
populate/check the archive cache, then `scripts/submit-debian-iteration.py` for
the BKC CLI/core job. Each component/run gets a new source extraction with
Debian patches followed by the ordered local series; source/object trees are
never reused across iterations. See [iteration details](docs/debian-iterations.md).
