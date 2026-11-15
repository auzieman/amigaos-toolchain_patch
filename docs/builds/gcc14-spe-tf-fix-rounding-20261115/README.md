# GCC14 SPE: round toward zero in the TF->SI conversion (#31) — 2026-11-15

## Defect

Converting IBM long double to (unsigned) long long gave 0 for some large values. On the A1222, `ld2ull((long double)(2^63-1))` returned 0, and `gcc.c-torture/execute/conversion.c` aborted at `-O0`. At -O2/-O3 its constants fold at compile time, which hid the defect.

Stepping through libgcc2's `__fixunstfDI` for a = 2^63-1 (`{hi 2^63, lo -1}`) showed the failing step: b = a / 2^32 = `{2^31, -2^-32}`, and `(unsigned) b` returned 0 instead of 0x7fffffff.

## Cause

`spe_fix_trunctfsi2_internal` (`gcc/config/powerpcspe/spe.md`), byte-identical to GCC 8.5, is documented as "add with rounding towards 0". Its template was:

```
mfspefscr %3 ; rlwinm %4,%3,0,0,29 ; ori %4,%4,1 ; efdadd %2,%1,%L1 ; mtspefscr %3 ; efdctsiz %0, %2
```

It computes the round-toward-zero SPEFSCR value in %4 but never writes it. So `efdadd hi+lo` runs in the current mode, round-to-nearest. 2^31 - 2^-32 then rounds up to 2^31, which `efdctsiz` cannot represent. The defect is latent upstream; GCC 9 dropped the backend with it in place.

## Fix

`patches/gcc/gcc14-spe-candidate/0021-set-round-toward-zero-in-tf-to-si-conversion.patch` inserts `mtspefscr %4` before the `efdadd` and changes the length from 24 to 28. The emitted sequence becomes `mfspefscr; rlwinm; ori 7,7,1; mtspefscr 7; efdadd; mtspefscr 10; efdctsiz`.

`scripts/check-gcc14-spe-candidate.py` gains `tf-fix-rounding-regression`. It compiles `(unsigned) long double` at `-O2` and requires every `ori rN,rN,1` in the sequence to be followed by `mtspefscr rN`. It fails on the 0001-0019 compiler and passes with 0021.

## Validation

Prototype (0001-0019 tree + 0020 + 0021, compiler and libgcc rebuilt), A1222, static, -O0/-O2/-O3:
- `conversion.c`: pass at all levels (was abort at -O0); `20080502-1` (#36): pass.
- `ld2ull(2^63-1) = 0x7fffffffffffffff`, `ld2ull(2^63) = 0x8000000000000000`, `ld2ull/ld2sll(0x7ffffffffffff000) = 0x7ffffffffffff000`. These are identical to the Debian hard-float build.
- `__fixunstfDI` steps: `(unsigned){2^31,-2^-32} = 0x7fffffff`, then `(unsigned)(2^32-1) = 0xffffffff`.

## Rebuild with 0001-0021

A fresh tree was prepared with `scripts/prepare-gcc14-spe-candidate.py` (series 0001-0021), and the full stage1 / glibc 2.41 / final C/C++ toolchain was rebuilt from it.

- `scripts/check-gcc14-spe-candidate.py --qemu qemu-ppc`: 22/22.
- Per-issue checks, all pass:
  - `check-spe-vec-perm-reduction.py` (#29);
  - `check-spe-tf-pack-overlap.py` (#36);
  - `check-spe-tf-fix-rounding.py` (#31).
- bench/ probes, static:
  - A1222: all pass, including spe-abi-smoke 9/9 (directed rounding).
  - qemu-ppc e500v2: all pass except rounding, the known QEMU gap (#3).
- On the A1222, the `-O3` int sum matches a scalar reference for n = 0..1001, and the `ld2ull`/`ld2sll` values match the hard-float build at -O0 and -O2.
- GCC 14.2 gcc.c-torture execute + ieee (1724 tests, static), run on the A1222:

  | | compiled | passed | failed |
  |---|---|---|---|
  | -O0 | 1719 | 1719 | 0 |
  | -O2 | 1719 | 1719 | 0 |
  | -O3 | 1720 | 1720 | 0 |

  The only compile difference against Debian's hard-float powerpc-linux-gnu-gcc 14 is `ieee/cdivchkld.c` at -O2 (#30). The hard-float baseline itself aborts on cdivchkld at run time, while SPE passes it at -O0 and -O3.

Limits: static binaries only, and no Debian packaging or sbuild roots. #30 remains open.
