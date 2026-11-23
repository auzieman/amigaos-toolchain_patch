#!/usr/bin/env python3
"""Issue #46: BIT_INSERT_EXPR constant folding must use big-endian bit positions.

GCC 14.2.0's fold_ternary_loc folded BIT_INSERT_EXPR constants with the
little-endian bit position on BYTES_BIG_ENDIAN targets (GCC PR middle-end/116997,
fixed on releases/gcc-14 by b51b45eaf713, candidate 0024). On SPE the SLP
vectorizer folds bit-field stores that way, so each bit lands at 15 - i. Mesa's
ACO Operand flags were the visible victim (control 0x6400 became 0x0026).

Two programs are built static at -O0, -O2 and -O3 and run under qemu-ppc -cpu
e500v2. qemu is adequate here because the code is integer only.
- ACO's Operand flag layout in C: every operand must read back 0x6400.
- GCC's own gcc.dg/vect/pr116997.c, which aborts on the bug.
"""
import argparse, json, subprocess
from pathlib import Path

OPERAND = r"""
#include <stdio.h>
struct op {
   unsigned data;
   unsigned short reg;
   union {
      struct { unsigned char isTemp : 1, isFixed : 1, isPrecolored : 1, isConstant : 1, isKill : 1, isUndef : 1,
               isFirstKill : 1, isLateKill : 1, isClobbered : 1, isCopyKill : 1, isVectorAligned : 1,
               is16bit : 1, is24bit : 1, signext : 1, constSize : 2; };
      unsigned short control;
   };
};
static inline struct op undef_op(unsigned rc)
{
   struct op o = { 0 };
   o.isUndef = 1; o.data = rc << 24; o.isFixed = 1; o.isPrecolored = 1; o.reg = 128 << 2;
   return o;
}
int main(void)
{
   struct op v[4];
   for (unsigned i = 0; i < 4; i++) v[i] = undef_op(1);
   int bad = 0;
   for (unsigned i = 0; i < 4; i++) {
      printf("%04x ", v[i].control);
      bad |= v[i].control != 0x6400 || !v[i].isUndef || !v[i].isFixed;
   }
   printf("\n");
   return bad;
}
"""
PR116997 = r"""
struct S0 { unsigned f0; signed f2 : 11; signed : 6; } GlobS, *Ptr = &GlobS;
const struct S0 Initializer = {7, 3};
int main (void)
{
  for (unsigned i = 0; i <= 2; i++)
    *Ptr = Initializer;
  if (GlobS.f2 != 3)
    __builtin_abort ();
  return 0;
}
"""
FLAGS = ["-mcpu=8548", "-mabi=spe", "-mspe", "-mfloat-gprs=double", "-static"]

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--compiler", type=Path, required=True)
p.add_argument("--qemu", type=Path, required=True)
p.add_argument("--output", type=Path, required=True)
a = p.parse_args()
a.output.mkdir(parents=True, exist_ok=False)
cc = a.compiler.resolve()
runs, passed = {}, True
for name, src in [("operand", OPERAND), ("pr116997", PR116997)]:
    c = a.output / f"{name}.c"
    c.write_text(src)
    for opt in ["-O0", "-O2", "-O3"]:
        exe = a.output / f"{name}{opt}"
        build = subprocess.run([str(cc), *FLAGS, opt, str(c), "-o", str(exe)], capture_output=True, text=True)
        if build.returncode:
            runs[f"{name} {opt}"] = {"build": build.stderr[-300:]}
            passed = False
            continue
        run = subprocess.run([str(a.qemu), "-cpu", "e500v2", str(exe)], capture_output=True, text=True, timeout=60)
        runs[f"{name} {opt}"] = {"exit": run.returncode, "stdout": run.stdout.strip()}
        passed &= run.returncode == 0
r = {"issue": 46, "compiler": subprocess.run([str(cc), "--version"], capture_output=True, text=True).stdout.splitlines()[0],
     "runs": runs, "passed": passed}
(a.output / "result.json").write_text(json.dumps(r, indent=2) + "\n")
print(json.dumps(r))
raise SystemExit(0 if passed else 1)
