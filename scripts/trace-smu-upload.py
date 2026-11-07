#!/usr/bin/env python3
"""Model reviewed smu7 upload word decoding + writel serialization, not hardware."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('firmware', type=Path)
a = p.parse_args()
data = a.firmware.read_bytes()
if len(data) < 32:
    p.error('short common firmware header')
size, offset = struct.unpack_from('<II', data, 20)
if size % 4 or offset + size > len(data):
    p.error('invalid firmware payload bounds/alignment')
payload = data[offset:offset + size]
words = [payload[i:i + 4] for i in range(0, size, 4)]

def stream(host, explicit_le):
    # Reviewed C: native *src versus le32_to_cpu(*src); writel sends LE.
    return b''.join(int.from_bytes(w, 'little' if explicit_le else host)
                    .to_bytes(4, 'little') for w in words)

reference = stream('little', False)
results = {}
for name, host, explicit in [('x86-baseline', 'little', False),
                              ('ppc-be-baseline', 'big', False),
                              ('ppc-be-explicit-le', 'big', True)]:
    out = stream(host, explicit)
    mismatch = [i for i in range(len(words)) if out[4*i:4*i+4] != reference[4*i:4*i+4]]
    results[name] = {'first_register_value': hex(int.from_bytes(out[:4], 'little')),
                     'serialized_prefix': out[:16].hex(' '),
                     'stream_sha256': hashlib.sha256(out).hexdigest(),
                     'different_words_from_x86': len(mismatch),
                     'first_different_word': mismatch[0] if mismatch else None}
print(json.dumps({'model_only': True, 'hardware_readback': False,
                  'firmware_sha256': hashlib.sha256(data).hexdigest(),
                  'payload_offset': offset, 'payload_bytes': size,
                  'upload_start': '0x20000', 'results': results}, indent=2))
