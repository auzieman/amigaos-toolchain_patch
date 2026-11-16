# radeonsi, amdgpu and dEQP built with the GCC14 SPE SDK on the A1222 (#44) — 2026-11-16

## Question

The A1222 GL bundle that passed dEQP GLES2 on 2026-11-15 (radeonsi with ACO and no LLVM, softpipe, EGL surfaceless/GBM, kernel 017 with `polaris11_le_user_ib=1`) was built with Debian's hard-float `powerpc-linux-gnu-gcc-14`. The P1022's e500v2 has no classic FPU, so every FP instruction in that bundle trapped into the kernel's emulator.

Does the same stack build and work when compiled for SPE with the policy-pinned SDK, `tabor-spe-toolchain 14.2.0+tabor2` (`powerpc-linux-gnuspe`)?

## Method: change only the compiler

- **The same inputs as the hard-float bundle:**
  - The same Mesa 26.2.3 tree with its big-endian GPU-model changes, at `--buildtype=release`, with `-Dllvm=disabled -Damd-use-llvm=false`, `radeonsi,softpipe`, EGL and GBM, GLES2.
  - The same libdrm 2.4.134 and zlib 1.4, and the same VK-GL-CTS 1.4.6.2 `deqp-gles2` with the same big-endian dEQP patches.
- **Every library in the processes is SPE code:** glibc 2.41, libm, libstdc++, libgcc_s and libatomic come from the GCC14 SPE packages.
  - libgallium contains 56,717 `efd`/`efs`/`evfs` instructions and no classic FPU instruction (`objdump -M e500x2`).
  - libm contains 15,141.
- **The bundle** (`/opt/a1222-gl-spe`, 53 MB, `a1222-gl-spe.tar.xz` sha256 `962ddb4005925b60…`) ran from a RAM tmpfs. Nothing was installed on the board. The kernel was 6.12.113-tabor-e2e-017 after a cold boot, with amdgpu loaded with `polaris11_le_user_ib=1`.

## Results on the A1222 (P1022 e500v2, RX 550 Polaris11)

| test | SPE build | hard-float build |
|---|---|---|
| gltest, softpipe | clear and draw pass, 0/4096 bad pixels | not run on the board |
| gltest, radeonsi (`AMD Radeon RX 550 Series (radeonsi, polaris11, ACO, DRM 3.61)`) | clear and draw pass, 0/4096 bad pixels | pass |
| kmstest (GBM + EGL + GLES2 on KMS, legacy ADDFB) | GL readback of all four quadrants correct; cube 600 frames at 59.72 fps, 0 flip errors | 59.63 fps |
| dEQP GLES2 mustpass, 17,165 cases | 17,041 Pass, 111 NotSupported, 10 QualityWarning, 3 CompatibilityWarning, **0 Fail** | 17,040 Pass, 1 Fail, the same 111/10/3 |
| dEQP wall time | **1,959 s** in one pass, watchdog on | 60,617 s plus a 15,226 s rerun of 769 cases with the watchdog off |
| kernel taint, GPU timeouts or faults | 0, none | 0, none |

Compared case by case, the 17,165 results agree everywhere except `dEQP-GLES2.functional.rasterization.limits.points`. That case is the dEQP big-endian defect the hard-float run found and its patch 0033 fixes. The SPE build includes the patch, so it passes. The NotSupported, QualityWarning and CompatibilityWarning cases are the same ones as on hard float:

- NotSupported: no depth16 + separate stencil8 FBO, no multisample config, and three extensions.
- QualityWarning: AMD's major-axis line interpolation.
- CompatibilityWarning: the flush/finish readback-time heuristic.

The full non-Pass list is `deqp-gles2-non-pass.txt`, and the per-chunk timeline is `deqp-gles2-summary.txt`. The complete results list has sha256 `bd2e9dc6d8501c55…`.

The 125 cases from the five slowest hard-float chunks (texture mipmap/vertex filtering and the fragment_ops stencil groups) took about 2,684 s on hard float, and one chunk hit the 600 s timeout. On SPE they took 40 s. Across the whole mustpass, the SPE build is about 39 times faster. This is the cost of the FPU emulation, not a GPU difference.

## Debian Mesa 25.0.7 under the same SDK (compile only)

Debian's Mesa 25.0.7-2+deb13u1 source, with its `debian/patches` series applied, compiles cleanly with tabor2 and Debian's default `dpkg-buildflags` (`-g -O2 -fstack-protector-strong …`). It was configured with radeonsi (ACO, `-Damd-use-llvm=false`) and softpipe, no LLVM, EGL/GBM, against the GCC14 sbuild packages of libdrm 2.4.124, expat, zstd, zlib and elfutils. That is 1,215 of 1,215 build steps, with no compiler error. Debian's own `debian/rules` builds only softpipe on powerpcspe (powerpcspe is not in `LLVM_ARCHS`), so enabling radeonsi there needs a rules change. It was not run on the board.

## Kernel and amdgpu under the same SDK (compile only)

The kernel 017 source and `.config` build with `CROSS_COMPILE=powerpc-linux-gnuspe-` (`vmlinux modules dtbs`, `make` exit 0):

- `olddefconfig` adds only three `is not set` lines: `GCC_PLUGIN_LATENT_ENTROPY`, `RANDSTRUCT_FULL` and `RANDSTRUCT_PERFORMANCE`.
- The build prints one warning, a `-Wdiscarded-qualifiers` in `gfx_v8_0.c:884` (`gfx_v8_0_ring_test_ring`).
- tabor2 accepts the kernel's `-mno-spe -mspe=no -msoft-float -mcpu=8540 -mno-altivec` (`V=1` on an amdgpu object).
- `amdgpu.ko` contains no SPE or FPU instruction. vmlinux has 69 `ev*` instructions, which are the SPE context save/restore and emulation code.

This kernel was not booted. The board ran the hard-float-built kernel 017.

## Limits

- GLES2 only. GLES3 dEQP, desktop GL and X/E clients were not run.
- The SPE run used the same dEQP patches as the hard-float one. dEQP's own reference rendering is now SPE code too, so an SPE floating-point error common to both sides could hide in a comparison. None of the results differ.
- #41 (an SPE overflow that sometimes saturates instead of becoming Inf) did not show up here.
