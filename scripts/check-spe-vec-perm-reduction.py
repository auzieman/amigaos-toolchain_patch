#!/usr/bin/env python3
"""Issue #29: an -O3 integer reduction must compile (V2SI vec_perm_const operands).

The vectorizer's reduction epilogue permutes the accumulator with a constant
zero vector; without forced registers the SPE backend ICEs. Compiles a plain
int sum at -O3 and requires success plus SPE vector adds in the output.
Compile-only; run-time behaviour is checked on the A1222 separately.
"""
import argparse, json, re, subprocess
from pathlib import Path

SOURCE = "int sum(const int *p, int n)\n{ int s = 0; for (int i = 0; i < n; i++) s += p[i]; return s; }\n"
FLAGS = ["-mcpu=8548", "-mabi=spe", "-mspe", "-mfloat-gprs=double", "-mlong-double-128", "-O3", "-S"]

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--compiler", type=Path, required=True)
p.add_argument("--output", type=Path, required=True)
a = p.parse_args()
a.output.mkdir(parents=True, exist_ok=False)
src, asm = a.output / "vsum.c", a.output / "vsum.s"
src.write_text(SOURCE)
cc = subprocess.run([str(a.compiler.resolve()), f"-B{a.compiler.resolve().parent}/", *FLAGS,
                     str(src), "-o", str(asm)], capture_output=True, text=True)
(a.output / "compile.stderr.txt").write_text(cc.stderr)
text = asm.read_text() if asm.exists() else ""
r = {"issue": 29, "compile_exit": cc.returncode, "ice": "internal compiler error" in cc.stderr,
     "evaddw": bool(re.search(r"\bevaddw\b", text)),
     "passed": cc.returncode == 0 and bool(re.search(r"\bevaddw\b", text))}
(a.output / "result.json").write_text(json.dumps(r, indent=2) + "\n")
print(json.dumps(r))
raise SystemExit(0 if r["passed"] else 1)
