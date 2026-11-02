#!/usr/bin/env python3
"""Package the recorded native SPE cross compiler under its own Debian identity."""
import argparse, hashlib, json, os, re, shutil, subprocess, tarfile
from pathlib import Path
p = argparse.ArgumentParser(description=__doc__)
for name in ['project', 'tools', 'cache', 'compiler-receipt', 'output']:
    p.add_argument('--' + name, type=Path, required=True)
p.add_argument('--version', default='8.5.0+tabor1')
a = p.parse_args(); assert re.fullmatch(r'8\.5\.0\+tabor[1-9][0-9]*', a.version)
a.output.mkdir(parents=True, exist_ok=False)
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
spec = json.loads((a.project / 'profiles/toolchain-bootstrap.json').read_text())
archive = a.cache / spec['gcc']['filename']
assert hashlib.sha512(archive.read_bytes()).hexdigest() == spec['gcc']['sha512']
original = json.loads(a.compiler_receipt.read_text())
assert original['source_sha512'] == spec['gcc']['sha512']
assert original['status'] == 'reference-cxx-runtime-built-not-executed'
assert original['target'] == spec['target']
cc1=Path(subprocess.check_output([str(a.tools/'bin/powerpc-linux-gnuspe-gcc'),'-print-prog-name=cc1'],text=True).strip()).resolve()
assert cc1.is_relative_to(a.tools.resolve())
root = a.output / 'root'; target = root / 'usr/lib/tabor-spe-toolchain'
shutil.copytree(a.tools, target, symlinks=True)
# Libtool archives retain the original bootstrap install prefix. Consumers then
# embed /tools RUNPATHs even after GCC itself has been relocated correctly.
# Shared/static libraries remain; .la files are not required by the compiler.
removed_libtool_archives = []
for archive_file in sorted(target.rglob('*.la')):
    removed_libtool_archives.append(str(archive_file.relative_to(target)))
    archive_file.unlink()
binpath = root / 'usr/bin'; binpath.mkdir(parents=True)
for tool in sorted((target / 'bin').iterdir()):
    assert tool.name.startswith('powerpc-linux-gnuspe-')
    (binpath / tool.name).symlink_to('../lib/tabor-spe-toolchain/bin/' + tool.name)
licenses = root / 'usr/share/doc/tabor-spe-toolchain'; licenses.mkdir(parents=True)
with tarfile.open(archive) as tar:
    for name in ['COPYING', 'COPYING3', 'COPYING.LIB', 'COPYING3.LIB', 'COPYING.RUNTIME']:
        entry = tar.getmember('gcc-8.5.0/' + name)
        assert entry.isfile()
        (licenses / name).write_bytes(tar.extractfile(entry).read())
(licenses / 'provenance.json').write_text(json.dumps({'gcc_source': spec['gcc'],
    'compiler_receipt_sha256': sha(a.compiler_receipt),
    'frontend_sha256': sha(cc1), 'compiler_sha256': sha(a.tools / 'bin/powerpc-linux-gnuspe-gcc')}, indent=2) + '\n')
(licenses / 'compiler-build-receipt.json').write_text(json.dumps(original, indent=2)+'\n')
control = root / 'DEBIAN'; control.mkdir()
(control / 'control').write_text(f'''Package: tabor-spe-toolchain
Version: {a.version}
Architecture: amd64
Multi-Arch: foreign
Maintainer: Tabor lab <root@localhost>
Depends: libc6, libgmp10, libmpfr6, libmpc3, zlib1g, binutils-powerpc-linux-gnu (>= 2.38)
Description: Recorded native GCC 8.5 SPE cross compiler
 Historical reference compiler for the experimental powerpcspe port.
 Contains actual compiler files, not a dummy build-dependency package.
 Target sysroot and installed target libc packages are separate inputs.
''')
package = a.output / ('tabor-spe-toolchain_' + a.version + '_amd64.deb')
subprocess.run(['dpkg-deb', '--root-owner-group', '-Zgzip', '-Snone', '--build', root, package], check=True)
(a.output / 'receipt.json').write_text(json.dumps({'status': 'native-toolchain-package-built-not-installed',
    'version': a.version, 'recipe_sha256': sha(Path(__file__)), 'compiler_receipt_sha256': sha(a.compiler_receipt),
    'frontend_sha256': sha(cc1), 'compiler_sha256': sha(a.tools / 'bin/powerpc-linux-gnuspe-gcc'),
    'package_sha256': sha(package), 'bytes': package.stat().st_size,
    'removed_libtool_archives': removed_libtool_archives,
    'target_runtime_package': False}, indent=2) + '\n')
print(package)
