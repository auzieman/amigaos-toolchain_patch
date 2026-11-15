#!/usr/bin/env python3
"""Issue #36: *frob_tf_ti must not overwrite its TI input while packing a TF value.

Compiles the gcc.c-torture/execute/20080502-1 pattern at -O2 and fails if a
consecutive evmergelo pair reads the register that the first one wrote.
Compile-only; run-time behaviour is checked on the A1222 separately.
"""
import argparse, json, re, subprocess
from pathlib import Path

SOURCE = ("long double __attribute__((noinline)) f(long double x)\n"
          "{ return __builtin_signbit(x) ? 3.1415926535897932384626433832795029L : 0.0; }\n"
          "int g(void) { return f(-1.0L) != 3.1415926535897932384626433832795029L; }\n")
FLAGS = ["-mcpu=8548", "-mabi=spe", "-mspe", "-mfloat-gprs=double", "-mlong-double-128", "-O2", "-S"]

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--compiler", type=Path, required=True)
p.add_argument("--output", type=Path, required=True)
a = p.parse_args()
a.output.mkdir(parents=True, exist_ok=False)
src, asm = a.output / "tf-pack.c", a.output / "tf-pack.s"
src.write_text(SOURCE)
cc = subprocess.run([str(a.compiler.resolve()), f"-B{a.compiler.resolve().parent}/", *FLAGS,
                     str(src), "-o", str(asm)], capture_output=True, text=True)
text = asm.read_text() if asm.exists() else ""
pairs = re.findall(r"evmergelo (\d+),\d+,\d+\s*\n\s*evmergelo \d+,(\d+),(\d+)", text)
bad = [list(x) for x in pairs if x[0] in x[1:]]
r = {"issue": 36, "compile_exit": cc.returncode, "pairs": len(pairs), "overlapping": bad,
     "passed": cc.returncode == 0 and bool(pairs) and not bad}
(a.output / "result.json").write_text(json.dumps(r, indent=2) + "\n")
print(json.dumps(r))
raise SystemExit(0 if r["passed"] else 1)
