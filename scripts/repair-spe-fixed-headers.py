#!/usr/bin/env python3
"""Repair GCC8 machine_name fixincludes corruption of quoted Linux paths.

Keep generated GCC fixes and compiler-owned limits headers; change only the
five demonstrated __has_include string operands. Run while staging the SDK.
"""
import argparse
import hashlib
import json
from pathlib import Path

HEADERS = {'sys/mount.h': 'mount.h', 'sys/rseq.h': 'rseq.h',
           'bits/sched.h': 'sched/types.h', 'bits/statx.h': 'stat.h',
           'bits/unistd_ext.h': 'close_range.h'}

def repair(root):
    records = []
    for relative, linux in HEADERS.items():
        path = root / relative
        before = path.read_bytes()
        bad = ('__has_include ("__linux__/' + linux + '")').encode()
        good = ('__has_include ("linux/' + linux + '")').encode()
        assert before.count(bad) == 1, 'Unexpected generated header: ' + str(path)
        after = before.replace(bad, good)
        path.write_bytes(after)
        records.append({'file': relative, 'before_sha256': hashlib.sha256(before).hexdigest(),
                        'after_sha256': hashlib.sha256(after).hexdigest()})
    return records

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', type=Path)
    p.add_argument('--receipt', type=Path, required=True)
    a = p.parse_args()
    a.receipt.write_text(json.dumps(repair(a.root), indent=2) + '\n')
