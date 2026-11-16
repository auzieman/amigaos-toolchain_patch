#!/usr/bin/env python3
"""Replica-local: derive a GCC14 sbuild spec from the final zlib spec. Not a project script."""
import argparse, hashlib, json, subprocess
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument('package'); p.add_argument('--lock', required=True); p.add_argument('--cache', required=True)
p.add_argument('--dep', action='append', default=[], help='work/<job> whose powerpcspe packages are inputs')
p.add_argument('--binnmu', type=int, default=0); p.add_argument('--series'); p.add_argument('--profiles'); p.add_argument('--out', required=True)
a = p.parse_args(); B = Path('/srv/data1/tabor-build/linux-live-001'); P = Path('/home/tabor/amigaos-toolchain_patch')
s = json.load(open('/srv/data1/tabor-build/specs/zlib-gcc14-binnmu-local.json'))
for k in ['source_patch', 'binary_nmu']: s.pop(k, None)
s.update(package=a.package, source_lock=a.lock, source_cache=a.cache, required_full_rebuild=True,
         scope=f'GCC14 powerpcspe sbuild consumer (#27): Debian {a.package}. Built against the stage2 glibc 2.41: rebuild after the full glibc.')
if a.binnmu: s['binary_nmu'] = a.binnmu
if a.profiles: s['build_profiles'] = a.profiles
if a.series: s['quilt_patch_series'] = {'path': a.series, 'sha256': hashlib.sha256((P / a.series).read_bytes()).hexdigest()}
for d in a.dep:
    rec = f'{d}/receipt.json'; r = json.load(open(B / rec))
    pk = sorted({n.split('_', 1)[0] for n in r['packages'] if n.endswith('_powerpcspe.deb') and '-dbgsym_' not in n})
    s['extra_receipts'].append({'receipt': rec, 'sha256': hashlib.sha256((B / rec).read_bytes()).hexdigest(), 'packages': pk})
json.dump(s, open(a.out, 'w'), indent=2); print('spec', a.out)
