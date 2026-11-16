# #46: BIT_INSERT_EXPR folding on big-endian (GCC PR116997), candidate 0024 — 2026-11-16

## Failure

In #44's GLES3 dEQP run on the A1222, the radeonsi bundle built with `tabor-spe-toolchain 14.2.0+tabor2` crashed in 21 chunks (the `fragdepth.*` and `texture_functions.*` groups, 525 cases with no result).

- With ACO's validator: `Uninitialized Operand: exp %9, (%0, %0, %0) en:r*** mrtz`.
- With validation off: `aco_scheduler_ilp.cpp:515 add_entry: Assertion 'op.isFixed()'`.

The same Mesa source built with Debian's hard-float `powerpc-linux-gnu-g++-14` passes these cases. The NIR before ACO is identical in the two builds.

## Reduction

ACO's `Operand` holds its flags as `uint8_t` bit-fields in an anonymous struct, unioned with `uint16_t control_`. `aco-operand-bits.cpp` reproduces that layout. An undefined operand must have isUndef, isFixed and isPrecolored set, which is `control_ = 0x6400` with big-endian, MSB-first bit-fields.

| compiler and flags | control_ |
|---|---|
| tabor2 `-O0`, `-O1` | `0x6400` |
| tabor2 `-O2`, `-O3` | **`0x0026`**: each set bit `i` moved to `15 - i` |
| tabor2 `-O2 -fno-tree-slp-vectorize`, `-O3 -fno-tree-sra` | `0x6400` |
| Debian `powerpc-linux-gnu-g++` 14.2.0-19, `-O1`/`-O2`/`-O3` | `0x6400` |
| tabor3 (this change), `-O2`/`-O3` | `0x6400` |

The `-O2` tree dumps show the cause:

- **tabor2** folds the flag stores through `BIT_INSERT_EXPR` into `MEM <vector(2) short unsigned int> = { 512, 38 }`, where 38 = 0x26 (`tree-optimized-O2-tabor2.txt`).
- **Debian's hard-float compiler** emits one 32-bit store of `0x02006400` (`tree-optimized-O2-debian-hardfloat.txt`).

## Cause

This is GCC PR middle-end/116997. `fold_ternary_loc` folded `BIT_INSERT_EXPR` constants with the little-endian bit position on `BYTES_BIG_ENDIAN` targets.

- The fix is on trunk as 2e30e90a0c2b, and on releases/gcc-14 as **b51b45eaf713** (2024-11-18). It is in 14.3 but not in 14.2.0.
- `scripts/build-gcc14-spe-sdk.sh` extracts the upstream `gcc-14.2.0` tarball from Debian's `gcc-14_14.2.0-19` source and does not apply Debian's patches.
- Debian's `git-updates.diff` (the 14 branch to 2025-03-15, f8504e361c8) carries this fix, so Debian's own compilers are correct.
- rs6000 without AltiVec never vectorises these stores, so the hard-float control does not reach the bad fold. The SPE target does.

## Fix: `patches/gcc/gcc14-spe-candidate/0024-fold-bit-insert-expr-big-endian-pr116997.patch`

This is the two-line hunk of b51b45eaf713 alone, against the 14.2.0 `gcc/fold-const.cc:13631`:

```c
	  if (BYTES_BIG_ENDIAN)
	    bitpos = TYPE_PRECISION (type) - bitpos - bitsize;
```

`series` and `manifest.json` list it after 0023.

## Evidence

- **`scripts/check-spe-bit-insert-fold.py` (new).** It builds the Operand layout in C, and GCC's own `gcc.dg/vect/pr116997.c`, static at -O0/-O2/-O3, and runs them under `qemu-ppc -cpu e500v2`. This is integer code, so qemu is adequate.
  - tabor2 fails: `0026` at -O2 and -O3 (`check-tabor2.json`).
  - tabor3 passes at every level (`check-tabor3.json`).
  - pr116997.c passes with both compilers on this target, so it is kept only as a regression guard.
- **No other code change.** The GCC torture `execute` and `execute/ieee` suites were compiled at -O0/-O2/-O3 with tabor2 and tabor3 in one container with the target headers. All 4,830 compiles give identical assembly, and 342 fail with both alike (`torture-asm-tabor2-vs-tabor3.txt`).
- **Existing checks.** `check-gcc14-spe-candidate.py` passes 22/22 with `--qemu` (the #3-patched qemu-ppc) and 20/20 without. The five `check-spe-*` scripts pass (`*-tabor3.json`, `candidate-checks-tabor3*.log`).
- **SDK.** `build-gcc14-spe-sdk.sh` was run package-managed (`PREFIX=/usr/lib/tabor-spe-toolchain INSTALLED_SYSROOT=/ MULTIARCH=1`) with 0001-0024. `package-gcc14-spe-host-toolchain.py --version 14.2.0+tabor3` then gives `tabor-spe-toolchain_14.2.0+tabor3_amd64.deb`, sha256 `a7283c9c6cab16af…` (`tabor-spe-toolchain-receipt.json`). `profiles/compiler-policy.json` is **not** changed here; re-pinning is the owner's call.
- **A1222.** The unmodified Mesa source, dEQP and the test programs were rebuilt with tabor3 (`/opt/a1222-gl-spe3`, kernel 017, `polaris11_le_user_ib=1`). They reran the 2,087 GLES3 cases that tabor2 had failed, warned on, or crashed before reporting. On tabor2, 21 of those chunks crashed. On tabor3, **0 crashed**, and all 393 `fragdepth.*` and `texture_functions.*` cases pass.
  - The rerun (4,346 s) gave 500 Pass, 1,016 Fail and 496 QualityWarning. The 1,016 Fails are 1,008 `texture.wrap.astc_*` and 8 `common.fract` highp. The QualityWarnings are all `builtin_functions.precision.*`. Both groups are covered under "What remains" below.
  - The list had 22 duplicate lines, so dEQP refused three chunks ("Duplicate test case"). Their 53 `precision.*` cases were rerun from a de-duplicated list.
  - Hard-float control: libgallium rebuilt with tabor2 and `-fno-tree-slp-vectorize` on every object also passes the crashing cases.

### What remains, and is not this bug

- **`texture.wrap.astc_*` fails with tabor3 and with the hard-float bundle alike.** It is a big-endian bug in the CPU ASTC path of the Mesa tree used here, not a compiler fault.
- **`builtin_functions.common.fract` highp (8 Fail) and the `builtin_functions.precision.*` QualityWarnings** remain on tabor3, but pass with the hard-float bundle. They are separate SPE effects on dEQP's CPU reference side. For `fract`, the e500v2 single-precision add/sub gives an exact zero the sign of its first operand, so the reference expects -0 where the GPU correctly returns +0. Tracked separately.
