# GCC14 SPE: multi-register move pieces of under-aligned MEMs (#30) — 2026-11-15

## Defect

`gcc.c-torture/execute/ieee/cdivchkld.c` crashed the compiler at `-O2`:

```
during RTL pass: split2
internal compiler error: Segmentation fault
mark_label_nuses (emit-rtl.cc:3896) <- try_split (emit-rtl.cc:4093) <- split_all_insns
```

`cvise` reduced it to six lines. A `_Complex long double` is passed through an unprototyped call, so it is stored to an outgoing argument slot:

```c
double match_c, match_zi_0;
_Complex long double match_z;
void match() {
  match_z = match_zi_0;
  match(match_c, match_z);
}
```

The unfixed compiler crashes on this at `-O1`, `-O2`, `-O3` and `-Os`, not only `-O2`; `-O0` compiles.

## Cause

The insn being split was

```
(set (mem:TF (plus:SI (reg/f:SI 1) (const_int 8)) [0 S16 A32])
     (reg:TF 16))                                   {*movtf_softfloat}
```

`*movtf_softfloat` splits through `rs6000_split_multireg_move`, which builds each DFmode piece with `simplify_gen_subreg (DFmode, dst, TFmode, offset)`. The second piece came back as NULL, so the splitter emitted `(set (nil) (reg:DF 17))`, and `try_split`'s `mark_label_nuses` dereferenced the NULL.

Linux SPE defaults to `-mstrict-align` (`linuxspe.h` `TARGET_DEFAULT`), and `sysv4.h` defines `STRICT_ALIGNMENT` as `TARGET_STRICT_ALIGN`. GCC 14's `simplify_subreg` refuses to make a MEM subreg aligned below the outer mode on strict-alignment targets:

```c
      && !(STRICT_ALIGNMENT && MEM_ALIGN (op) < GET_MODE_ALIGNMENT (outermode))
```

Here the slot is A32 and DFmode needs 64 bits. GCC 8.5's `simplify_subreg` had no such clause and returned `adjust_address_nv (op, outermode, byte)`, which the restored splitter relies on. The bug was found with an `-O0 -g`, `--enable-checking=yes,rtl` build of cc1 under gdb.

## Fix

`patches/gcc/gcc14-spe-candidate/0022-split-multireg-mem-pieces-without-strict-align-subreg.patch` adds `rs6000_split_multireg_piece`. For a MEM it applies GCC 8's rule: no mode-dependent address and the volatile condition, then `adjust_address_nv`. It uses `simplify_gen_subreg` otherwise, and all nine piece computations in `rs6000_split_multireg_move` call it. Register operands behave as before.

The pieces are `evstdd`/`evldd` at the slot's offsets, as GCC 8 emitted. Outgoing argument slots are 8-byte aligned at run time because the SVR4 stack is 16-byte aligned. A genuinely misaligned TF MEM would behave as it did with GCC 8.

`scripts/check-spe-tf-split-misaligned.py` compiles the reduced case at `-O1`/`-O2`/`-O3`/`-Os`. It fails at all four levels with 0001-0021 and passes with 0022.

## Validation

Prototype (0001-0021 tree + 0022, `all-gcc`), on the A1222, static, with `-lm`:
- `cdivchkld` passes at `-O0`, `-O1`, `-O2`, `-O3` and `-Os`, the same as the 0001-0021 builds at `-O0`/`-O3`.
- Debian's hard-float baseline aborts on this test at run time.

## Rebuild with 0001-0022

A fresh tree was prepared with `scripts/prepare-gcc14-spe-candidate.py` (series 0001-0022), and the full stage1 / glibc 2.41 / final C/C++ toolchain was rebuilt from it.

- `scripts/check-gcc14-spe-candidate.py --qemu qemu-ppc`: 22/22.
- Per-issue checks, all pass:
  - `check-spe-vec-perm-reduction.py` (#29);
  - `check-spe-tf-pack-overlap.py` (#36);
  - `check-spe-tf-fix-rounding.py` (#31);
  - `check-spe-tf-split-misaligned.py` (#30).
- bench/ probes, static:
  - A1222: all pass, including spe-abi-smoke 9/9.
  - qemu-ppc e500v2: all pass except directed rounding (#3).
- GCC 14.2 gcc.c-torture execute + ieee (1724 tests, static), run on the A1222:

  | | SPE compiled | Debian hard float compiled | SPE passed |
  |---|---|---|---|
  | -O0 | 1719 | 1719 | 1719 |
  | -O2 | 1720 | 1720 | 1720 |
  | -O3 | 1720 | 1720 | 1720 |

  There are no compile differences between SPE and the hard-float baseline, and no SPE run-time failures. The remaining compile failures are shared by both compilers: options or effective targets the simple torture harness does not supply.

Limits: static binaries only, and no Debian packaging or sbuild roots.
