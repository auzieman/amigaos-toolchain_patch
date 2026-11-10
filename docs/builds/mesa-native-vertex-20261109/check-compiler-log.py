"""No-op pixel failures are expected; compiler failures are never acceptable."""
import argparse,json,re
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('log',type=Path);args=parser.parse_args()
text=args.log.read_text(errors='replace')
errors=[line for line in text.splitlines() if re.search(r'ACO ERROR|LLVM ERROR|NIR validation failed|never defined|Unimplemented NIR|Assertion .* failed|qemu: uncaught',line)]
ran=bool(re.search(r'Probe color|PIGLIT:|TABOR_IB_|TABOR_FETCH_',text))
print(json.dumps({'compiler_gate':'PASS' if ran and not errors else 'FAIL','workload_evidence':ran,'errors':errors,'gpu_execution_tested':False},indent=2))
raise SystemExit(int(not ran or bool(errors)))
