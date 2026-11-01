# A1222 roadmap for Steven and Hyperion

Working baseline: 2026-11-01, private collaboration. The aim is a reproducible
SPE-capable Linux reference plus evidence and compiler work usable by the
AmigaOS4 team. Feature/performance parity is an objective, not a result.

## Gates and ownership

| Gate | Linux reference and acceptance | AmigaOS4 follow-through |
| --- | --- | --- |
| Reproducible compiler | Pinned GCC8.5 reference, SPE double-GPR and IBM128 long double; actual host package and source/patch hashes | Hyperion confirms SDK tuple, compiler revision, data layouts and runtime. Pin adtools/container inputs independently. |
| CPU/compiler correctness | Arithmetic, varargs, libm/fenv, register/context preservation, atomics and exception smoke | Adapt portable probes to the selected OS4 runtime. Verify instruction emission, stack/register conventions and calls across SDK boundaries on A1222. |
| Runtime correctness | Restore Linux glibc2.41 SPE support; Debian package/runtime gates. Current blockers: rounding #3 and unwind #9 | Linux glibc/syscalls are not replacements for newlib/clib2/clib4. Confirm OS4 fenv, exception model, task switches and context preservation with Hyperion. |
| Kernel/board | Debian6.12.113-1 compiles; QEMU boot of earlier profile proven. New disk-root profile and physical board still pending | Hyperion owns OS4 kernel integration. Identify required SPE enable/state preservation and board changes against their sources; no kernel-source access assumed. |
| Installed system | Essential closure, genuine dpkg installation, maintainer scripts/triggers, init, SSH, PAM, D-Bus, logind and persistent ext4 root | Use OS4-native packaging and service lifecycle. Carry over test methodology, not Debian setup scripts. |
| Physical graphics | Verify actual RAM, both cores, MMU, Radeon firmware/driver, Xorg, E, glxinfo renderer, gears and readback | OS4 drivers/graphics API require independent validation. Linux Mesa/Radeon success cannot certify OS4 drivers. |
| Performance | Matched fractal workload/images with timings, repetitions, instruction audit and environment hashes; software vs explicit SPE | Compile the same workload for OS4 with supported runtime, verify equal outputs, compare on same board/settings. Do not compare QEMU timing with hardware speed. |
| Product tuning | After physical acceptance, measure CPU/RAM/graphics and tune. Then port AlpinE tooling as Debian packages; Flatpak excluded | Select OS4 improvements from measured bottlenecks and feasible SDK/kernel work; agree priorities with Steven. |

## Immediate engineering order

1. Reduce and repair the compiler/libc unwind regression (#9), retaining
   baseline/candidate evidence. Keep the fenv rounding failure (#3) visible.
2. Fresh patched libc rebuild, normal package build checks, dynamic ABI and
   C++ regression tests. Stage2 bootstrap must be followed by full-feature libc.
3. Build/configure Essential dependency closure without fake package records or
   suppressed Debian configuration; boot persistent QEMU disk root and verify
   package database, services, SSH keys and reboot persistence.
4. Add the VM132-derived session dependency closure, Xorg/E and GL demos.
   Diagnose compositor errors separately (#8); retain renderer and frame results.
5. Validate USB boot files and board profile, then prepare the agreed SanDisk
   candidate. Physical A1222 acceptance precedes tuning and AlpinE ports.

## Information needed from Hyperion for the OS4 branch

- Exact failing AmigaGCConDocker image digest, command, output and intended
  SDK/runtime; see [integration review](amigagccondocker-integration.md).
- Expected SPE ABI and exception model, long-double format, runtime/library
  boundaries, and supported way to test FP/context state across tasks/signals.
- A maintainer who can build/test necessary OS4 kernel/runtime changes and
  return hardware logs. We do not have OS4 kernel sources or a validated patch.

These inputs do not block the Linux work. Keep OS4 compiler/runtime patches in
its own branch and component series with licenses, exact inputs, reproducer,
expected output, build receipt and physical test evidence. Publish progress in
this private repository; do not expose proprietary media, SDKs or kernel code.

## Evidence and issue navigation

- [Current Debian libc evidence](builds/glibc-debian-20261101/)
- [Bootstrap package/root plan](../profiles/images/trixie-bootstrap.json)
- [Rounding issue #3](https://github.com/auzieman/amigaos-toolchain_patch/issues/3)
- [Integration issue #7](https://github.com/auzieman/amigaos-toolchain_patch/issues/7)
- [Compositor issue #8](https://github.com/auzieman/amigaos-toolchain_patch/issues/8)
- [Unwind issue #9](https://github.com/auzieman/amigaos-toolchain_patch/issues/9)

## Verified increment: libc004

The protected-PIC compiler return-address correction now passes18 reduced
QEMU cases; fresh Debian libc004 passes the original C++ exception/RAII test
and a rebuilt C++ binary with matching new runtimes. See
[007 runtime result](builds/glibc-debian-20261101/007-runtime-result.md).
The rounding failure remains. For OS4, inspect its actual selected backend
and exception model before considering an analogous patch; the inactive-
backend mistake and corrected selection are preserved in the evidence trail.

## Debian build-system direction

The Linux lane follows the [Debian-first build contract](debian-port-build-contract.md):
patched foundations, real package repositories/build roots, source Build-Depends
for scheduling and binary dependencies for installation. Recent fresh-source
[preflight evidence](builds/debian-dependency-preflight-20261101/README.md)
identifies the actual next gates. The current wrapper preserves Debian build
commands but is not yet a full apt/sbuild dependency service.
