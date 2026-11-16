#!/usr/bin/env python3
"""Check that a cross-built libicudata holds ICU common data in the target's byte order.

A little-endian build host cross-building ICU for big-endian powerpcspe used to emit
the data container in host order, word-swapped, and every ICU program on the target
then failed with U_INVALID_FORMAT_ERROR (patches/icu/0001-cross-endian-data-library.patch).
This reads the icudtNN_dat symbol from the library and checks the ICU data header:
magic da27, the CmnD format, and isBigEndian matching the ELF's byte order.
"""
import argparse, re, subprocess, sys

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('library', help='libicudata.so.NN.N (ELF)')
p.add_argument('--readelf', default='readelf')
a = p.parse_args()

def readelf(*args):
    return subprocess.check_output([a.readelf, '-W', *args, a.library], text=True)

big_endian = 'big endian' in readelf('-h')
symbol = next(l.split() for l in readelf('-s').splitlines()
              if re.search(r'\bicudt\d+_dat$', l))
value = int(symbol[1], 16)
data = open(a.library, 'rb').read()
for line in readelf('-S').splitlines():
    m = re.search(r'\]\s+(\S+)\s+\S+\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)', line)
    if m and int(m[2], 16) <= value < int(m[2], 16) + int(m[4], 16):
        offset = int(m[3], 16) + value - int(m[2], 16)
        break
else:
    sys.exit('icudt symbol not inside any section')
header = data[offset:offset + 16]
order = 'big' if big_endian else 'little'
checks = {
    'magic da27': header[2:4] == b'\xda\x27',
    'isBigEndian matches ELF': header[8] == int(big_endian),
    'format CmnD': header[12:16] == b'CmnD',
    'header size sane': 16 <= int.from_bytes(header[0:2], order) <= 256,
}
print(symbol[-1], header.hex(), 'ELF', order + '-endian')
for name, ok in checks.items():
    print(('ok   ' if ok else 'FAIL ') + name)
sys.exit(0 if all(checks.values()) else 1)
