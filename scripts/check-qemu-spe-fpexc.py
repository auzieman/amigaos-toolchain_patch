#!/usr/bin/env python3
"""Issue #39: qemu-user must answer PR_GET_FPEXC/PR_SET_FPEXC on SPE as the kernel does.

Builds bench/spe-fpexc-prctl.c static with the given SPE compiler, runs it under the given
qemu-ppc (linux-user) as -cpu e500v2, and requires the prctl answers the physical A1222 gives
(docs/builds/qemu-fpexc-prctl-20261118/hw/board-fpexc-020.txt), a written fegetenv mode word,
and an overflow that still gives inf after sqrt().
"""
import argparse, json, re, subprocess
from pathlib import Path

FLAGS = ["-mcpu=8548", "-mabi=spe", "-mspe", "-mfloat-gprs=double", "-mlong-double-128",
         "-O2", "-g0", "-static", "-pthread"]
# Lines whose prctl results must match the A1222 exactly (SPEFSCR values are not compared:
# the kernel starts programs with 0x3c and sets sticky bits that qemu does not).
EXPECT = [
    ("start: PR_GET_FPEXC", "rc=0 errno=0  val=0x3"),
    ("PR_SET_FPEXC 0x20080", "rc=0 errno=0"),
    ("after SW_ENABLE|OVF", "rc=0 errno=0  val=0x20080"),
    ("thread: PR_GET_FPEXC", "rc=0 errno=0  val=0x20080"),
    ("PR_SET_FPEXC 0xff0080", "rc=0 errno=0"),
    ("after SW_ENABLE|0xff0000 (masked)", "rc=0 errno=0  val=0x1f0080"),
    ("PR_SET_FPEXC 0x2", "rc=0 errno=0"),
    ("after classic 2", "rc=0 errno=0  val=0x2"),
    ("PR_SET_FPEXC 0x4", "rc=-1 errno=22"),
    ("after invalid 4", "rc=0 errno=0  val=0x2"),
]

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--compiler", type=Path, required=True)
p.add_argument("--sysroot", type=Path)
p.add_argument("--qemu", type=Path, required=True, help="qemu-ppc (linux-user)")
p.add_argument("--output", type=Path, required=True)
a = p.parse_args()
a.output.mkdir(parents=True, exist_ok=False)
source = Path(__file__).resolve().parents[1] / "bench/spe-fpexc-prctl.c"
binary = a.output / "spe-fpexc-prctl"
sysroot = [f"--sysroot={a.sysroot}"] if a.sysroot else []
cc = subprocess.run([str(a.compiler), *sysroot, *FLAGS, str(source), "-lm", "-o", str(binary)],
                    capture_output=True, text=True)
(a.output / "build.log").write_text(cc.stdout + cc.stderr)
out = ""
if cc.returncode == 0:
    run = subprocess.run([str(a.qemu), "-cpu", "e500v2", str(binary)],
                         capture_output=True, text=True, timeout=120)
    out = run.stdout + run.stderr
(a.output / "qemu.txt").write_text(out)
lines = {l[:34].rstrip(): l[34:].strip() for l in out.splitlines() if len(l) > 34}
checks = {tag: lines.get(tag) == want.strip() for tag, want in EXPECT}
env = re.search(r"^fegetenv rc=(\S+) env words (\S+) ", out, re.M)
checks["fegetenv mode word"] = bool(env) and env.group(1) == "0" and env.group(2) == "0x3"
checks["overflow after sqrt"] = bool(re.search(r"^sqrt=.* big\*ten=inf$", out, re.M))
r = {"issue": 39, "compile_exit": cc.returncode, "checks": checks,
     "passed": cc.returncode == 0 and all(checks.values())}
(a.output / "result.json").write_text(json.dumps(r, indent=2) + "\n")
print(json.dumps(r))
raise SystemExit(0 if r["passed"] else 1)
