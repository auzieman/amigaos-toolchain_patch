#!/usr/bin/env python3
"""Issue #38: -fzero-call-used-regs must compile on SPE and clear whole GPRs.

Without an rs6000 TARGET_ZERO_CALL_USED_REGS hook, every function compiled with
-fzero-call-used-regs=used-gpr (Debian openssl's flag) ICEd in change_address_1.
This compiles a small function set at -O0 and -O2 for each zeroing mode. Each
compile must succeed. For used-gpr every function must clear its call-clobbered
GPRs with `evxor rN,rN,rN` (all 64 bits) before the return, never touching the
return registers r3/r4. Compile-only.
"""
import argparse, json, re, subprocess
from pathlib import Path

SOURCE = """
int g(int);
int call(int a) { return g(a) + 1; }
double h(double);
double dcall(double a, double b) { return h(a * b) + a; }
long long leaf(long long a, long long b) { return a * b + (a >> 3); }
int loop(const int *v, int n) { int s = 0; for (int i = 0; i < n; i++) s += v[i] * (i + 1); return s; }
"""
FLAGS = ["-mcpu=8548", "-mabi=spe", "-mspe", "-mfloat-gprs=double", "-mlong-double-128", "-S"]
MODES = ["used-gpr", "used", "all-gpr", "all", "used-gpr-arg", "used-arg", "all-arg"]

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--compiler", type=Path, required=True)
p.add_argument("--output", type=Path, required=True)
a = p.parse_args()
a.output.mkdir(parents=True, exist_ok=False)
src = a.output / "zcur.c"
src.write_text(SOURCE)
cc = a.compiler.resolve()
compiles, failures = {}, []
for mode in MODES:
    for opt in ["-O0", "-O2"]:
        asm = a.output / f"zcur-{mode}{opt}.s"
        run = subprocess.run([str(cc), f"-B{cc.parent}/", *FLAGS, opt, f"-fzero-call-used-regs={mode}",
                              str(src), "-o", str(asm)], capture_output=True, text=True)
        compiles[f"{mode} {opt}"] = run.returncode
        if run.returncode:
            failures.append({"mode": mode, "opt": opt,
                             "error": next((l for l in run.stderr.splitlines()
                                            if "error" in l or "sorry" in l), run.stderr[-200:])})
functions = {}
asm = a.output / "zcur-used-gpr-O2.s"
text = asm.read_text() if asm.exists() else ""
for name in ["call", "dcall", "leaf", "loop"]:
    body = re.search(rf"^{name}:\n(.*?)\n\s*blr", text, re.S | re.M)
    tail = body.group(1) if body else ""
    cleared = sorted({int(n) for n in re.findall(r"evxor (\d+),\1,\1", tail)})
    return_regs = {3, 4} if name == "leaf" else {3}
    functions[name] = {"cleared_gprs": cleared, "clears_return_reg": bool(return_regs & set(cleared))}
ok_functions = all(f["cleared_gprs"] and not f["clears_return_reg"] for f in functions.values())
r = {"issue": 38, "compiles": compiles, "failures": failures, "used_gpr_O2": functions,
     "passed": not failures and ok_functions}
(a.output / "result.json").write_text(json.dumps(r, indent=2) + "\n")
print(json.dumps({k: r[k] for k in ("failures", "used_gpr_O2", "passed")}))
raise SystemExit(0 if r["passed"] else 1)
