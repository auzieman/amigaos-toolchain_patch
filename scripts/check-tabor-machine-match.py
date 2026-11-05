#!/usr/bin/env python3
"""Reject a Tabor machine source whose compatible cannot match its DTB.

Run before packaging a board kernel; this checks source/DT identity, not
execution or whether the supplied source was used to build a particular ELF.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--machine-source', type=Path, required=True)
p.add_argument('--dtb', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
assert not a.output.exists(), 'Refusing existing evidence output'
source = a.machine_source.read_text()
machine = re.search(r'define_machine\(tabor\)\s*(?:=\s*)?\{(.*?)\n\};', source, re.S)
assert machine, 'Expected Tabor machine definition'
match = re.search(r'\.compatible\s*=\s*"([^"]+)"', machine[1])
assert match, 'Review machine selection semantics before extending this check'
compatible = subprocess.check_output(['fdtget', '-t', 's', str(a.dtb), '/', 'compatible'], text=True).strip().split()
r = {'status': 'passed' if match[1] in compatible else 'failed',
     'machine_compatible': match[1], 'dtb_compatibles': compatible,
     'machine_source_sha256': hashlib.sha256(a.machine_source.read_bytes()).hexdigest(),
     'dtb_sha256': hashlib.sha256(a.dtb.read_bytes()).hexdigest(),
     'kernel_execution_validated': False, 'physical_boot': False}
a.output.parent.mkdir(parents=True, exist_ok=True)
a.output.write_text(json.dumps(r, indent=2)+'\n')
print(json.dumps(r, indent=2))
raise SystemExit(0 if r['status'] == 'passed' else 1)
