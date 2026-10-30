#!/usr/bin/env python3
"""Verify recorded local inputs without applying patches or altering sources."""
from pathlib import Path
import hashlib,json,subprocess
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'docs/intake.json').read_text())
for item in data['files']:
    p=Path(item['path'])
    if hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']:
        raise SystemExit('Input mismatch: '+str(p))
board=Path(data['board_repository'])
upstream=board/'upstream/linux-5.4-rc3'
head=subprocess.check_output(['git','-C',str(upstream),'rev-parse','HEAD'],text=True).strip()
if head!=data['linux_baseline_commit']:raise SystemExit('Baseline revision mismatch')
subprocess.run(['git','-C',str(upstream),'apply','--check',str(board/'vendor/a-eon-5.4-rc3-a1222/tabor_5.4-1.patch')],check=True)
print('Input hashes and baseline patch applicability pass; no build claimed')
