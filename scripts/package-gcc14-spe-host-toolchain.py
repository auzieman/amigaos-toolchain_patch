#!/usr/bin/env python3
"""Package the GCC14 SPE cross compiler from build-gcc14-spe-sdk.sh as tabor-spe-toolchain.

Input is a package-managed build (PREFIX=/usr/lib/tabor-spe-toolchain INSTALLED_SYSROOT=/
MULTIARCH=1): it compiles against the installed libc6-dev:powerpcspe multiarch files, not a
private sysroot. The bootstrap sysroot and libtool archives are left out. Builds one native
.deb; target runtimes and libc are separate packages. Nothing is installed or executed
for the target.
"""
import argparse, datetime, hashlib, json, os, re, shutil, subprocess
from pathlib import Path

PREFIX = Path('/usr/lib/tabor-spe-toolchain')
T = 'powerpc-linux-gnuspe'
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--project', type=Path, required=True, help='this repository')
p.add_argument('--sdk', type=Path, required=True, help='WORK/out/usr/lib/tabor-spe-toolchain')
p.add_argument('--gcc-source', type=Path, required=True, help='prepared GCC14 tree (licenses)')
p.add_argument('--output', type=Path, required=True)
p.add_argument('--version', default='14.2.0+tabor1')
a = p.parse_args()
assert re.fullmatch(r'14\.2\.0\+tabor[1-9][0-9]*', a.version), a.version
a.output.mkdir(parents=True, exist_ok=False)
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
gcc = a.sdk / 'bin' / (T + '-gcc')
q = lambda *args: subprocess.check_output([str(gcc), *args], text=True).strip()
facts = {'version': q('-dumpfullversion'), 'machine': q('-dumpmachine'),
         'sysroot': q('-print-sysroot'), 'multiarch': q('-print-multiarch')}
assert facts['version'] == '14.2.0' and facts['machine'] == T, facts
assert facts['sysroot'] in ('', '/') and facts['multiarch'] == T, facts
manifest = a.project / 'patches/gcc/gcc14-spe-candidate/manifest.json'
series = [x['file'] for x in json.loads(manifest.read_text())['patches']]

root = a.output / 'root'; target = root / PREFIX.relative_to('/')
shutil.copytree(a.sdk, target, symlinks=True,
                ignore=lambda d, names: ['sysroot'] if Path(d) == a.sdk else [])
removed = []
for la in sorted(target.rglob('*.la')):
    removed.append(str(la.relative_to(target))); la.unlink()
# Host (x86-64) executables carry full debug info; strip them. Target (PowerPC) objects stay.
stripped = []
for f in sorted(target.rglob('*')):
    if f.is_file() and not f.is_symlink() and f.read_bytes()[:4] == b'\x7fELF':
        if 'x86-64' in subprocess.check_output(['file', '-b', str(f)], text=True):
            subprocess.run(['strip', '--strip-unneeded', str(f)], check=True)
            stripped.append(str(f.relative_to(target)))
binpath = root / 'usr/bin'; binpath.mkdir(parents=True)
for tool in sorted((target / 'bin').iterdir()):
    assert tool.name.startswith(T + '-'), tool.name
    (binpath / tool.name).symlink_to('../lib/tabor-spe-toolchain/bin/' + tool.name)
cc1 = Path(q('-print-prog-name=cc1')).resolve()
assert cc1.is_relative_to(a.sdk.resolve()), cc1
doc = root / 'usr/share/doc/tabor-spe-toolchain'; doc.mkdir(parents=True)
for name in ['COPYING', 'COPYING3', 'COPYING.LIB', 'COPYING3.LIB', 'COPYING.RUNTIME']:
    shutil.copy(a.gcc_source / name, doc / name)
provenance = {'gcc': 'Debian gcc-14 14.2.0-19 DFSG + GCC 8.5 powerpcspe imports',
              'candidate_series': series, 'manifest_sha256': sha(manifest),
              'recipe': 'scripts/build-gcc14-spe-sdk.sh',
              'recipe_sha256': sha(a.project / 'scripts/build-gcc14-spe-sdk.sh'),
              'compiler_facts': facts, 'cc1_sha256': sha(cc1), 'gcc_sha256': sha(gcc)}
(doc / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
needed = set()
for f in [cc1, gcc, Path(q('-print-prog-name=cc1plus')).resolve()]:
    out = subprocess.check_output(['readelf', '-d', str(f)], text=True)
    needed |= set(re.findall(r'\(NEEDED\).*\[(.+)\]', out))
control = root / 'DEBIAN'; control.mkdir()
(control / 'control').write_text(f'''Package: tabor-spe-toolchain
Version: {a.version}
Architecture: amd64
Multi-Arch: foreign
Maintainer: Tabor lab <root@localhost>
Depends: libc6, libgmp10, libmpfr6, libmpc3, binutils-powerpc-linux-gnu (>= 2.44)
Description: GCC 14.2 SPE cross compiler for powerpcspe (e500v2)
 GCC 14.2.0 with the restored powerpcspe backend and candidate series
 {series[0][:4]}-{series[-1][:4]} (tabor). C and C++; compiles against the installed
 libc6-dev:powerpcspe multiarch files (sysroot /). Target runtimes and libc
 are separate packages.
''')
package = a.output / f'tabor-spe-toolchain_{a.version}_amd64.deb'
# Reproducible packaging: the same SDK tree gives the same .deb. Every mtime is
# clamped to the GCC release date (gcc/DATESTAMP), which dpkg-deb also uses.
stamp = (a.gcc_source / 'gcc/DATESTAMP').read_text().strip()
epoch = str(int(datetime.datetime.strptime(stamp, '%Y%m%d')
                .replace(tzinfo=datetime.timezone.utc).timestamp()))
for f in [root, *root.rglob('*')]:
    os.utime(f, (int(epoch), int(epoch)), follow_symlinks=False)
subprocess.run(['dpkg-deb', '--root-owner-group', '-Zxz', '--build', str(root), str(package)],
               check=True, env={**os.environ, 'SOURCE_DATE_EPOCH': epoch})
receipt = {'status': 'native-toolchain-package-built-not-installed', 'version': a.version,
           'package': package.name, 'package_sha256': sha(package), 'bytes': package.stat().st_size,
           'recipe_sha256': sha(Path(__file__)), 'compiler_facts': facts, 'needed_libraries': sorted(needed),
           'removed_libtool_archives': removed, 'stripped_host_executables': stripped,
           'provenance': provenance}
(a.output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(package)
