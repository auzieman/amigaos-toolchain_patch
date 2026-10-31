# AmigaGCConDocker applicability review — 2026-10-31

The user reports Steven may want this work for AmigaGCConDocker. The specific
failure, compiler version and intended runtime are not yet supplied. Modern
A1222/SPE support is a working hypothesis, not an established bug diagnosis.
No upstream changes, issue comments, image builds or SDK downloads were made.

## Inspected upstream snapshots

- [AmigaGCConDocker](https://github.com/walkero-gr/AmigaGCConDocker/tree/804b597413b6f047d632a7b2d6f364e693b9058c),
  commit `804b597413b6f047d632a7b2d6f364e693b9058c` (2026-10-24).
- [AmigaGCConDocker-base](https://github.com/walkero-gr/AmigaGCConDocker-base/tree/f50531301eeb86ab89bae19e9d55a3c4bcd7aea4),
  commit `f50531301eeb86ab89bae19e9d55a3c4bcd7aea4` (2026-10-17).

Both inspected repositories carry GPL version 3 license text. This does not
establish the licenses or redistribution rights of every bundled SDK/library.
Any reused component retains its own source notices and license requirements.

## Components and applicability

| Component | Source evidence | Consequence for our work |
| --- | --- | --- |
| Development image | [Dockerfile](https://github.com/walkero-gr/AmigaGCConDocker/blob/804b597413b6f047d632a7b2d6f364e693b9058c/ppc-amigaos/Dockerfile) copies `/opt/ppc-amigaos` from a compiler base image and a separate SDK image | Toolchain changes belong below this packaging layer first. |
| Existing SPE option | [Target documentation](https://github.com/walkero-gr/AmigaGCConDocker/blob/804b597413b6f047d632a7b2d6f364e693b9058c/docs/ppc-amigaos.md) explicitly advertises GCC6 for SPE/A1222 | Use its known advertised path as a reference; documentation is not a runtime test or proof that every other compiler lacks SPE. |
| Compiler sources | Base [dependency Dockerfile](https://github.com/walkero-gr/AmigaGCConDocker-base/blob/f50531301eeb86ab89bae19e9d55a3c4bcd7aea4/ppc-amigaos/Dockerfile.deps) clones `AmigaLabs/adtools` | Trace and pin adtools and its actual GCC/binutils inputs before patching. The dependency image currently imports moving repositories. |
| Compiler build | [compile-adtools.sh](https://github.com/walkero-gr/AmigaGCConDocker-base/blob/f50531301eeb86ab89bae19e9d55a3c4bcd7aea4/ppc-amigaos/scripts/compile-adtools.sh) uses gild to select GCC major and binutils, then native-build gcc-cross | Candidate compiler patch insertion is in this base/adtools build, with exact revisions and a constrained job count. |
| AmigaOS runtime contract | Target docs name newlib, clib2 and clib4; base [features.mk](https://github.com/walkero-gr/AmigaGCConDocker-base/blob/f50531301eeb86ab89bae19e9d55a3c4bcd7aea4/ppc-amigaos/misc/gcc-build/features.mk) selects SJLJ exceptions, disables TLS and enables AmigaOS threading for GCC8+ | Keep AmigaOS runtime, exceptions and threading decisions separate from Linux glibc assumptions. |
| Recent changes | [Changelog](https://github.com/walkero-gr/AmigaGCConDocker/blob/804b597413b6f047d632a7b2d6f364e693b9058c/ppc-amigaos/CHANGELOG.md) records GCC15/clib4 fixes, an SJLJ change reversal and later Mesa/clib4 library updates | Obtain the exact failing image digest and reproducer; do not infer which of these is Steven's problem. |

## What we can offer today

Our current reference is GCC8.5 targeting `powerpc-linux-gnuspe`. We have not
accepted a modern GCC SPE restoration patch: `patches/gcc/series` remains empty
apart from its status comment. Thus there is no completed modern compiler patch
to apply to adtools yet.

The three glibc patches restore Linux e500 sysdeps, shared selection/state and
current Linux internal syscall interfaces for Debian glibc2.41. They are not
drop-in patches for AmigaOS newlib/clib2/clib4. Linux board/DTS patches likewise
remain Linux-specific. Updating the container host's glibc cannot add SPE to its
AmigaOS cross-compiler.

The reusable material is our pinned-source/fresh-patch workflow, SPE arithmetic
and instruction checks, matched workload and ABI-test design. The Linux ABI
program itself includes Linux futex/syscall/ucontext interfaces and TLS, so it
must be adapted rather than assumed portable. Our Linux fenv test still fails
under QEMU; pthread/TLS awaits a futex-enabled kernel; C++ unwinding is untested.
The Linux long-double mismatch we found is a reason to measure AmigaOS data
layout independently, not a reason to force its compiler to our Linux flags.

## Bounded next action

1. Capture Steven's failing command, error/output, image digest, GCC version,
   selected C runtime and expected A1222 behavior.
2. Pin the corresponding adtools revision, GCC fork/ref, binutils and image
   digests; inspect the relevant target configuration, SPE backend and libgcc.
3. Reproduce the smallest compile/link failure in an isolated R730 container.
   Compare with the advertised GCC6 SPE image using matching SDK/runtime inputs.
4. For a confirmed modern compiler SPE gap, maintain a separate ordered compiler
   patch series and validate emitted instructions, calling conventions, varargs,
   runtime boundaries and exceptions. Then test the AmigaOS binary on A1222.
5. Package the proven compiler in the base image and rebuild the development
   image only after those gates. Keep Linux image builds independently active.

This review establishes an integration route, not a completed AmigaOS fix or a
claim that a Linux QEMU result validates the AmigaOS SDK.
