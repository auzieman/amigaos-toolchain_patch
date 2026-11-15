# GCC14 SPE: early-clobber on *frob_tf_ti (#36) — 2026-11-15

## Defect

`gcc.c-torture/execute/20080502-1.c` aborted at `-O2` and `-O3` on the A1222 every run. Debian's hard-float powerpc-linux-gnu-gcc 14 passes it. A returned IBM long double (r3-r6, spilled and reloaded as four words) is re-packed into two SPE doubles for `cmptfeq_gpr`:

```
	lwz 8,24(1)                       r8 = word 2
	lwz 6,16(1) / lwz 7,20(1) / lwz 9,28(1)
	evmergelo 8,6,7	 # *frob_tf_ti    r8 = {w0,w1}, overwrites word 2
	evmergelo 9,8,9                   r9 = {w1,w3}, should be {w2,w3}
```

libgcc's own `__fixtfdi` contained the same pair (`evmergelo r8,r6,r7; evmergelo r9,r8,r9`), so signed long double -> long long conversion was wrong too. For example, `(long long)(long double)0x7ffffffffffff000` returned 0.

## Cause

`*frob_tf_ti` (`gcc/config/powerpcspe/spe.md`) is unchanged from GCC 8.5. Its template writes `%0` before it reads `%Y1`/`%Z1`, but operand 0 is `=r`, not early-clobber. GCC 14's register allocator assigned the TF output r8:r9 over the TI input r6:r7:r8:r9. GCC 8's allocator evidently did not, so the defect was latent.

The other multi-instruction frob patterns (`*frob_ti_tf`, `*frob_ti_tf_2`, `*frob_di_<mode>`) already use `=&r`. The single-instruction ones read all inputs in one instruction.

## Fix

`patches/gcc/gcc14-spe-candidate/0020-early-clobber-tf-from-ti-subreg-output.patch` changes operand 0 of `*frob_tf_ti` to `=&r`. With it the pair becomes `evmergelo 8,4,5; evmergelo 9,6,7` (disjoint).

`scripts/check-gcc14-spe-candidate.py` gains `tf-pack-overlap-regression`. It compiles the test's pattern at `-O2` and fails if a consecutive `evmergelo` pair reads the register the first one wrote. It fails on the 0001-0019 compiler and passes with 0020.

## Validation (prototype: 0001-0019 tree + 0020 + 0021, compiler and libgcc rebuilt)

On the A1222, static:
- `20080502-1`: pass at -O0/-O2/-O3, against abort at -O2/-O3 before.
- `(long long)(long double)0x7ffffffffffff000`: correct (was 0).
- `__fixtfdi` in the rebuilt libgcc.a: `evmergelo r8,r4,r5; evmergelo r9,r6,r7`.

The unsigned conversion `ld2ull(2^63-1)` still returned 0 with 0020 alone. That is a separate defect, #31, fixed by 0021: see [gcc14-spe-tf-fix-rounding-20261115](../gcc14-spe-tf-fix-rounding-20261115/README.md). The fresh-tree rebuild and the full validation of 0001-0021 are recorded there.
