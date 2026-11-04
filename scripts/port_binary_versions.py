"""Read native Debian binary-only rebuild levels for coinstallable libraries.

Use Debian's binNMU version convention; never rewrite built package control
fields. sbuild owns the actual binary-only rebuild and changelog metadata.
"""
import re
from debian.deb822 import Packages

def native_bin_nmus(index):
    levels = {}
    with index.open() as stream:
        for binary in Packages.iter_paragraphs(stream, use_apt_pkg=False):
            if binary.get('Architecture') != 'amd64' or binary.get('Multi-Arch') != 'same':
                continue
            version = binary['Version']
            match = re.fullmatch(r'(.+)\+b([0-9]+)', version)
            if not match:
                continue
            source = binary.get('Source', binary['Package'])
            name = source.split()[0]
            declared = re.search(r'\(([^)]+)\)', source)
            original = declared.group(1) if declared else match.group(1)
            if match.group(1) != original:
                continue
            key = (name, original)
            levels[key] = max(levels.get(key, 0), int(match.group(2)))
    return levels
