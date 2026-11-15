#!/usr/bin/env python3
"""Issue #31: the long double -> int conversion must round toward zero.

spe_fix_trunctfsi2_internal builds a round-toward-zero SPEFSCR value with
`ori rN,rN,1`; this check compiles (unsigned) long double at -O2 and fails
unless every such value is installed with `mtspefscr rN` before the efdadd.
Compile-only; run-time behaviour is checked on the A1222 separately.
"""
import argparse, json, re, subprocess
from pathlib import Path

SOURCE = "unsigned u32(long double a) { return (unsigned) a; }\n"
FLAGS = ["-mcpu=8548", "-mabi=spe", "-mspe", "-mfloat-gprs=double", "-mlong-double-128", "-O2", "-S"]

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--compiler", type=Path, required=True)
p.add_argument("--output", type=Path, required=True)
a = p.parse_args()
a.output.mkdir(parents=True, exist_ok=False)
src, asm = a.output / "tf-fix.c", a.output / "tf-fix.s"
src.write_text(SOURCE)
cc = subprocess.run([str(a.compiler.resolve()), f"-B{a.compiler.resolve().parent}/", *FLAGS,
                     str(src), "-o", str(asm)], capture_output=True, text=True)
text = asm.read_text() if asm.exists() else ""
seqs = re.findall(r"ori (\d+),\1,1\s*\n\s*(\w+) ?(\d*)", text)
bad = [list(x) for x in seqs if not (x[1] == "mtspefscr" and x[2] == x[0])]
r = {"issue": 31, "compile_exit": cc.returncode, "sequences": len(seqs), "missing_mtspefscr": bad,
     "passed": cc.returncode == 0 and bool(seqs) and not bad}
(a.output / "result.json").write_text(json.dumps(r, indent=2) + "\n")
print(json.dumps(r))
raise SystemExit(0 if r["passed"] else 1)
