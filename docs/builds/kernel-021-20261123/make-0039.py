#!/usr/bin/env python3
"""Patch 0039: demote the amdgpu/powerplay bring-up trace prints to debug level.

Kernel 016 logs INIT_TRACE/PWR_TRACE/SMU_DIAG/SMU_CALIB at info level (148,681
lines in one 3.8-day boot, kmsg overruns, all written to the root USB stick).
Only the print calls change: dev_info -> dev_dbg, pr_info -> pr_debug, on calls
whose format string starts with one of the tags. Values computed for the prints
outside the call are unchanged. With CONFIG_DYNAMIC_DEBUG they can be turned
back on, e.g. dyndbg="file smu7_smumgr.c +p" or amdgpu.dyndbg=+p.

usage: make-0039.py SOURCE_TREE   (edits in place, prints a unified diff)
"""
import difflib, re, sys
from pathlib import Path
TAGS = ('INIT_TRACE', 'PWR_TRACE', 'SMU_DIAG', 'SMU_CALIB')
CALL = re.compile(r'\b(dev_info|pr_info)\((?=[^;]*"(?:%s))' % '|'.join(TAGS))
FILES = ['drivers/gpu/drm/amd/amdgpu/amdgpu_ring.c',
         'drivers/gpu/drm/amd/amdgpu/amdgpu_device.c',
         'drivers/gpu/drm/amd/amdgpu/gfx_v8_0.c',
         'drivers/gpu/drm/amd/amdgpu/amdgpu_cgs.c',
         'drivers/gpu/drm/amd/pm/powerplay/smumgr/smu7_smumgr.c',
         'drivers/gpu/drm/amd/pm/powerplay/smumgr/polaris10_smumgr.c',
         'drivers/gpu/drm/amd/pm/powerplay/inc/pp_debug.h']
root = Path(sys.argv[1]); total = 0
for rel in FILES:
    path = root / rel; old = path.read_text()
    new, n = CALL.subn(lambda m: {'dev_info': 'dev_dbg', 'pr_info': 'pr_debug'}[m.group(1)] + '(', old)
    total += n
    if n:
        path.write_text(new)
        sys.stdout.writelines(difflib.unified_diff(old.splitlines(True), new.splitlines(True), 'a/' + rel, 'b/' + rel))
left = sum(len(re.findall(r'\b(?:dev_info|pr_info)\([^;]*"(?:%s)' % '|'.join(TAGS), (root / r).read_text())) for r in FILES)
print(f'# 0039: {total} calls demoted, {left} left', file=sys.stderr)
sys.exit(1 if total == 0 or left else 0)
