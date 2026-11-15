# GCC14 SPE: vec_perm_const operands forced to registers (#29) — 2026-11-15

## Defect

Any `-O3` integer reduction ended in an ICE:

```c
int sum(const int *p, int n)
{ int s = 0; for (int i = 0; i < n; i++) s += p[i]; return s; }
```

```
error: unrecognizable insn:
(set (reg:V2SI ...) (vec_select:V2SI (vec_concat:V4SI (reg:V2SI ...)
        (const_vector:V2SI [ (const_int 0 [0]) repeated x2 ]))
    (parallel [ (const_int 1 [0x1]) (const_int 2 [0x2]) ])))
during RTL pass: vregs
internal compiler error: in extract_insn, at recog.cc:2812
```

The GCC testsuite hits it at `-O3` in `gcc.c-torture/execute/20090113-1.c` and `pr94734.c`.

## Cause

The insn is the vectorizer's reduction epilogue: a whole-vector shift by one element, built as a permutation of the accumulator with a zero vector.

GCC 14's generic `expand_vec_perm_const` (`optabs.cc`) passes `v0`/`v1` to `TARGET_VECTORIZE_VEC_PERM_CONST` unchanged. They may be constants such as that `CONST0_RTX` vector. The generic code only forces them into registers after the hook declines. GCC 14's `config/rs6000/rs6000.cc` hook therefore starts with:

```c
  if (op0)
    {
      rtx nop0 = force_reg (vmode, op0);
      if (op0 == op1)
        op1 = nop0;
      op0 = nop0;
    }
  if (op1)
    op1 = force_reg (vmode, op1);
```

Candidate patch 0011 moved the restored `powerpcspe.cc` hook to the GCC 14 signature (`op_mode`) but did not add that block. For V2SI `[1 2]`, `rs6000_expand_vec_perm_const_1` accepts the permutation and emits `vec_select (vec_concat (reg, const_vector))`. The only matching pattern, `vec_perm10_v2si` (`evmergelohi`), requires `gpc_reg_operand` for both inputs.

## Fix

`patches/gcc/gcc14-spe-candidate/0019-force-vec-perm-const-operands-to-registers.patch` adds the same block to `rs6000_vectorize_vec_perm_const` in `powerpcspe.cc`.
- The query path (`testing_p`, null operands) is unchanged.
- The patch is appended to `series` and its sha256 recorded in `manifest.json`.
- 0011 is left as is.

`scripts/check-gcc14-spe-candidate.py` gains `vector-reduction-regression`, which compiles the loop above at `-O3`. On the pre-0019 compiler it is the only failing check (22/23); with 0019 all 23 pass.

## Validation

Toolchain: `development` 866dc1c recipe plus 0019. That is Debian gcc-14 14.2.0-19 DFSG, the 147 GCC 8.5 powerpcspe imports, candidate 0001-0019, glibc 2.41-12+deb13u4 + glibc 0001-0007 and Linux 6.12.113 UAPI headers, built stage1 -> glibc -> final C/C++ as in `gcc14-sdk-20261108/build.sh`. Runs were on a physical A1222 (kernel 6.12.113-tabor-e2e-017), with static binaries.

Prototype compiler (0001-0018 tree + this change, `all-gcc`):
- `sum()` compiles at `-O3` to `evldd`/`evaddw` with an `evmergelohi` shift against a zeroed register.
  Linked with a checker that compares against a scalar sum for n = 0..1001: 0 wrong on the A1222.
- `20090113-1` and `pr94734` compile at `-O3` and pass on the A1222.
- GCC 14.2 `gcc.c-torture/execute` + `execute/ieee` (1724 tests, static, `-w`; dg-options honoured, no .x drivers), SPE sets rebuilt and run on the A1222 with a 60 s limit:

  | | compiled | passed | failed |
  |---|---|---|---|
  | -O0 | 1719 | 1718 | `conversion` (#31) |
  | -O2 | 1719 | 1718 | `20080502-1` (long double, #36) |
  | -O3 | 1720 (was 1718) | 1719 | `20080502-1` |

  The only remaining compile difference against Debian's hard-float powerpc-linux-gnu-gcc 14 is `ieee/cdivchkld.c` at `-O2` (#30). There are no new failures.

## Rebuild

A fresh tree was prepared with `scripts/prepare-gcc14-spe-candidate.py` and the series 0001-0019. Patch 0019 applied, and 10 hunks on `powerpcspe.cc` were logged against 9 before. The full toolchain was then rebuilt: stage 1, glibc 2.41, and the final C/C++ compiler with libgcc_s, libstdc++ and libatomic.

- `scripts/check-gcc14-spe-candidate.py --qemu qemu-ppc`: 23/23 pass, including `vector-reduction-regression`.
- bench/ probes, static, flags as in `scripts/spe-abi-smoke.py` / `spe-cxx-smoke.py`:

  | probe | qemu-ppc e500v2 (10.0.13) | A1222 |
  |---|---|---|
  | spe-abi-smoke.c | 6/9: float/double directed rounding FAIL, the known QEMU gap (#3) | 9/9, `up=0x1.0000000000001p+0 float_up=0x1.000002p+0` |
  | spe-cxx-smoke.cpp | pass | pass |
  | atomic64-check.c, constructor-destructor-check.c, spe-return-address.c, spe-smp-check.c | pass | pass |
  | `sum()` at -O3 + checker (n = 0..1001) | pass | pass, 0 wrong |

  No binary contains classic FPU instructions.
- Torture, rebuilt with this toolchain and run on the A1222: SPE -O0/-O2/-O3 pass 1718/1718/1719, failing only `conversion` -O0 (#31) and `20080502-1` -O2/-O3 (#36). Compile results are identical to the prototype's: one difference against hard float, `ieee/cdivchkld.c` -O2 (#30).

Limits: static binaries only, and no Debian packaging or sbuild roots. #30, #31 and #36 remain open.
