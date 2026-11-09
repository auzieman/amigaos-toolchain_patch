"""Check retained canonical LE PM4 packet boundaries, not GPU execution."""
import argparse
import json
import struct
from pathlib import Path


def decode(data):
    if len(data) % 4:
        raise ValueError('partial dword')
    words = struct.unpack('<%dI' % (len(data) // 4), data)
    packets = []
    pos = 0
    while pos < len(words):
        header = words[pos]
        kind = header >> 30
        if kind == 2:
            size = 1
        elif kind in (0, 3):
            size = ((header >> 16) & 0x3fff) + 2
        else:
            raise ValueError(f'unsupported packet type {kind} at DW{pos}')
        if pos + size > len(words):
            raise ValueError(f'packet DW{pos} needs {size} words, only {len(words)-pos} remain')
        packet = {'offset_dw': pos, 'size_dw': size, 'type': kind}
        if kind == 3:
            packet['opcode'] = hex((header >> 8) & 0xff)
        packets.append(packet)
        pos += size
    return packets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', nargs='+', type=Path)
    args = parser.parse_args()
    results = []
    for path in args.files:
        try:
            packets = decode(path.read_bytes())
            results.append({'file': str(path), 'bounds': 'PASS', 'packets': packets})
        except ValueError as error:
            results.append({'file': str(path), 'bounds': 'FAIL', 'error': str(error)})
    print(json.dumps({'scope': 'packet framing only; payload semantics, mappings and hardware execution untested', 'results': results}, indent=2))
    return int(any(r['bounds'] == 'FAIL' for r in results))


if __name__ == '__main__':
    raise SystemExit(main())
