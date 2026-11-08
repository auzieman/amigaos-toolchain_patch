#!/usr/bin/env python3
"""Check a PPC32 BE module against a kernel release and optional export CRCs.

This never loads the module. Passing does not prove GPU or kernel behavior.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct


def inspect(path, release, symvers=None, reference=None):
    data = Path(path).read_bytes()
    if data[:7] != b"\x7fELF\x01\x02\x01" or len(data) < 52:
        raise ValueError("expected ELF32 big-endian version1")
    if struct.unpack_from(">HH", data, 16) != (1, 20):
        raise ValueError("expected PowerPC relocatable module")
    shoff = struct.unpack_from(">I", data, 32)[0]
    stride, count, names_index = struct.unpack_from(">HHH", data, 46)
    if stride != 40 or not count or names_index >= count or shoff + stride * count > len(data):
        raise ValueError("unsupported or truncated ELF section table")
    headers = [struct.unpack_from(">10I", data, shoff + i * stride) for i in range(count)]

    def payload(header):
        offset, size = header[4:6]
        if offset + size > len(data):
            raise ValueError("truncated ELF section")
        return data[offset:offset + size]

    names = payload(headers[names_index])
    sections = {}
    for header in headers:
        end = names.find(b"\0", header[0])
        if end < 0:
            raise ValueError("invalid section name")
        name = names[header[0]:end].decode("ascii")
        if name in (".modinfo", "__versions"):
            if name in sections:
                raise ValueError("duplicate metadata section")
            sections[name] = payload(header)
        if name.startswith("__version_ext_"):
            raise ValueError("extended modversions require a separate decoder")
    vermagic = [s.removeprefix(b"vermagic=").decode("ascii")
                for s in sections.get(".modinfo", b"").split(b"\0")
                if s.startswith(b"vermagic=")]
    if len(vermagic) != 1 or vermagic[0].split()[0] != release:
        raise ValueError("module vermagic does not match kernel release")
    if reference is not None:
        control = inspect(reference, release)
        if control["vermagic"] != vermagic[0]:
            raise ValueError("module vermagic flags differ from installed reference")
    result = {"elf": "ELF32-BE-PowerPC-REL", "vermagic": vermagic[0],
              "module_sha256": hashlib.sha256(data).hexdigest(),
              "export_crcs_checked": False, "hardware_validated": False}
    if symvers is not None:
        if "modversions" not in vermagic[0].split():
            raise ValueError("kernel module does not advertise modversions")
        expected = {}
        source = Path(symvers).read_bytes()
        for line in source.decode().splitlines():
            fields = line.split()
            if len(fields) < 4:
                raise ValueError("malformed Module.symvers")
            crc, symbol = int(fields[0], 16), fields[1]
            if symbol in expected and expected[symbol] != crc:
                raise ValueError("ambiguous kernel export CRC: " + symbol)
            expected[symbol] = crc
        versions = sections.get("__versions", b"")
        if not versions or len(versions) % 64:
            raise ValueError("missing or malformed PPC32 modversions")
        seen = set()
        for offset in range(0, len(versions), 64):
            record = versions[offset:offset + 64]
            crc = struct.unpack_from(">I", record)[0]
            end = record.find(b"\0", 4)
            if end < 0:
                raise ValueError("unterminated modversion symbol")
            symbol = record[4:end].decode("ascii")
            if not symbol or symbol in seen or expected.get(symbol) != crc:
                raise ValueError("kernel export CRC mismatch: " + symbol)
            seen.add(symbol)
        if "module_layout" not in seen:
            raise ValueError("module_layout ABI version missing")
        result.update(export_crcs_checked=True, versioned_symbols=len(seen),
                      kernel_symvers_sha256=hashlib.sha256(source).hexdigest())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module", type=Path)
    parser.add_argument("--kernel-release", required=True)
    parser.add_argument("--symvers", type=Path)
    parser.add_argument("--reference-module", type=Path)
    args = parser.parse_args()
    print(json.dumps(inspect(args.module, args.kernel_release, args.symvers,
                             args.reference_module), indent=2))


if __name__ == "__main__":
    main()
