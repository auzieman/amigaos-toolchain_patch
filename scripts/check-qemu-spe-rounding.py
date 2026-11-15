#!/usr/bin/env python3
"""Issue #3: SPE directed rounding must take effect under QEMU (SPEFSCR[FRMC]).

Builds bench/spe-abi-smoke.c static with the given SPE compiler, runs it with
`--cli` under the given qemu-ppc (linux-user) as -cpu e500v2, and requires the
float and double directed-rounding checks to pass. Patched QEMU is expected to
match the physical A1222 values (up=0x1.0000000000001p+0, float_up=0x1.000002p+0).
"""
import argparse, json, subprocess
from pathlib import Path

FLAGS = ["-mcpu=8548", "-mabi=spe", "-mspe", "-mfloat-gprs=double", "-mlong-double-128",
         "-O2", "-g0", "-frounding-math", "-static", "-pthread"]

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--compiler", type=Path, required=True)
p.add_argument("--sysroot", type=Path, required=True)
p.add_argument("--qemu", type=Path, required=True, help="qemu-ppc (linux-user)")
p.add_argument("--output", type=Path, required=True)
a = p.parse_args()
a.output.mkdir(parents=True, exist_ok=False)
source = Path(__file__).resolve().parents[1] / "bench/spe-abi-smoke.c"
binary = a.output / "spe-abi-smoke"
cc = subprocess.run([str(a.compiler), f"--sysroot={a.sysroot}", *FLAGS, str(source), "-lm",
                     "-o", str(binary)], capture_output=True, text=True)
(a.output / "build.log").write_text(cc.stdout + cc.stderr)
out = ""
if cc.returncode == 0:
    run = subprocess.run([str(a.qemu), "-cpu", "e500v2", str(binary), "--cli"],
                         capture_output=True, text=True, timeout=120)
    out = run.stdout + run.stderr
(a.output / "qemu.txt").write_text(out)
checks = {name: f"FENV_CHECK {name} PASS" in out for name in ("float_round", "double_round")}
detail = next((l for l in out.splitlines() if l.startswith("FENV_DETAIL")), "")
r = {"issue": 3, "compile_exit": cc.returncode, "checks": checks, "detail": detail,
     "passed": cc.returncode == 0 and all(checks.values())}
(a.output / "result.json").write_text(json.dumps(r, indent=2) + "\n")
print(json.dumps(r))
raise SystemExit(0 if r["passed"] else 1)
