#!/usr/bin/env python3
"""Issue #30: splitting a long double move to an A32 stack slot must not ICE.

A _Complex long double passed through an unprototyped call is stored to a
4-byte-aligned outgoing argument slot; rs6000_split_multireg_move then needs
DFmode pieces of that MEM, which GCC 14's strict-alignment subreg rules
refuse. Compiles the reduced case at -O1/-O2/-O3/-Os and requires success.
Compile-only; run-time behaviour is checked on the A1222 separately.
"""
import argparse, json, subprocess
from pathlib import Path

SOURCE = ("double match_c, match_zi_0;\n_Complex long double match_z;\n"
          "void match() {\n  match_z = match_zi_0;\n  match(match_c, match_z);\n}\n")
FLAGS = ["-mcpu=8548", "-mabi=spe", "-mspe", "-mfloat-gprs=double", "-mlong-double-128", "-w", "-S"]

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--compiler", type=Path, required=True)
p.add_argument("--output", type=Path, required=True)
a = p.parse_args()
a.output.mkdir(parents=True, exist_ok=False)
src = a.output / "tf-split.c"
src.write_text(SOURCE)
levels = {}
for opt in ["-O1", "-O2", "-O3", "-Os"]:
    cc = subprocess.run([str(a.compiler.resolve()), f"-B{a.compiler.resolve().parent}/", *FLAGS, opt,
                         str(src), "-o", str(a.output / f"tf-split{opt}.s")], capture_output=True, text=True)
    (a.output / f"tf-split{opt}.stderr.txt").write_text(cc.stderr)
    levels[opt] = {"exit": cc.returncode, "ice": "internal compiler error" in cc.stderr}
r = {"issue": 30, "levels": levels, "passed": all(v["exit"] == 0 for v in levels.values())}
(a.output / "result.json").write_text(json.dumps(r, indent=2) + "\n")
print(json.dumps(r))
raise SystemExit(0 if r["passed"] else 1)
