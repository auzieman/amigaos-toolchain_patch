#!/usr/bin/env python3
"""glibc patch 0008: e500v2 float zero sign in fmaf and ldexpf.

Usage: make-0008.py <glibc source tree after patches 0001-0007> <out.patch> <origin.json>

Single-precision efsadd on e500v2 gives (-0)+(-0) as +0 and a cancellation the first operand's
sign, and raises no exception. Two libm paths lean on IEEE float addition for a zero result:
  sysdeps/ieee754/dbl-64/s_fmaf.c   exact zero: return (float) temp + z;
  math/s_ldexp_template.c          zero or non-finite: return value + value;
Each is rewritten so the zero comes out unchanged on an IEEE host: the fmaf sum is done in
double, which e500v2 does in IEEE, and ldexp returns a zero as it is.
"""
import difflib, hashlib, json, sys
from pathlib import Path

src, out, origin = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
EDITS = {
    "sysdeps/ieee754/dbl-64/s_fmaf.c": (
        """  /* Ensure correct sign of an exact zero result by performing the
     addition in the original rounding mode in that case.  */
  if (temp == -z)
    return (float) temp + z;
""",
        """  /* Ensure correct sign of an exact zero result by performing the
     addition in the original rounding mode in that case.  The sum is
     formed in double: e500v2 single-precision addition gives
     (-0) + (-0) as +0 and a cancellation the first operand's sign.  */
  if (temp == -z)
    return (float) (temp + z);
"""),
    "math/s_ldexp_template.c": (
        """	if(!isfinite(value)||value==0) return value + value;
""",
        """	/* A zero is returned as it is: e500v2 single-precision addition
	   gives (-0) + (-0) as +0.  */
	if(value==0) return value;
	if(!isfinite(value)) return value + value;
"""),
}
diff, files = [], {}
for rel, (old, new) in EDITS.items():
    a = (src / rel).read_text(encoding="utf-8")
    if a.count(old) != 1:
        sys.exit(f"{rel}: anchor not found exactly once")
    b = a.replace(old, new)
    diff += difflib.unified_diff(a.splitlines(True), b.splitlines(True), "a/" + rel, "b/" + rel)
    files[rel] = {"baseline_sha256": hashlib.sha256(a.encode()).hexdigest(),
                  "patched_sha256": hashlib.sha256(b.encode()).hexdigest()}
head = """On e500v2, single-precision addition (efsadd) gives (-0) + (-0) as +0 and an
exact cancellation the sign of its first operand, and raises no SPE exception,
so no kernel fix-up runs. fmaf's exact-zero path, (float) temp + z, and the
ldexp template's value + value for a zero then return +0 where IEEE 754 and
C require -0: fmaf (-2, 1, 2) gave -0, ldexpf (-0.0, n) and asinf (-0.0),
which uses fmaf for tiny arguments, gave +0. Form the fmaf sum in double
(e500v2 double precision follows IEEE) and return a zero from ldexp as it is.
Both give the same values on an IEEE host.

"""
out.write_text(head + "".join(diff), encoding="ascii", newline="\n")
origin.write_text(json.dumps({
    "target": "glibc 2.41 after patches 1-7",
    "reason": "e500v2 efsadd zero sign: fmaf exact-zero result and ldexpf of -0",
    "status": "experimental; libm rebuilt and measured on the A1222",
    "files": files}, indent=2) + "\n", encoding="ascii", newline="\n")
print("wrote", out, origin)
