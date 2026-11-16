#!/usr/bin/env python3
"""Debhelper packaging of the GCC14 SPE target runtimes (libgcc_s, libstdc++, libatomic).

Takes the runtimes compiled by scripts/build-gcc14-spe-sdk.sh (package-managed build) and
builds tabor-spe-libgcc-s1 / tabor-spe-libstdc++6 / tabor-spe-libatomic1 for powerpcspe
with dpkg-buildpackage, using packaging/gcc14-runtime/debian. dh_shlibdeps needs the
target libc6:powerpcspe installed in the build root. This assembles recorded cross-build
output; it does not rebuild GCC or run target programs.
"""
import argparse, hashlib, json, re, shutil, subprocess
from pathlib import Path

T = 'powerpc-linux-gnuspe'
LIBS = {'libgcc_s.so.1': 'libgcc_s.so.1', 'libstdc++.so.6.0.33': 'libstdc++.so.6',
        'libatomic.so.1.2.0': 'libatomic.so.1'}
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--project', type=Path, required=True)
p.add_argument('--sdk', type=Path, required=True, help='WORK/out/usr/lib/tabor-spe-toolchain')
p.add_argument('--gcc-source', type=Path, required=True, help='prepared GCC14 tree (licenses)')
p.add_argument('--output', type=Path, required=True)
p.add_argument('--version', default='14.2.0+tabor1')
a = p.parse_args()
assert re.fullmatch(r'14\.2\.0\+tabor[1-9][0-9]*', a.version), a.version
a.output.mkdir(parents=True, exist_ok=False)
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
source = a.output / 'source'
shutil.copytree(a.project / 'packaging/gcc14-runtime/debian', source / 'debian')
runtime = source / 'runtime'; runtime.mkdir()
checked = {}
for name, soname in LIBS.items():
    lib = a.sdk / T / 'lib' / name
    header = subprocess.check_output(['readelf', '-h', str(lib)], text=True)
    dynamic = subprocess.check_output(['readelf', '-d', str(lib)], text=True)
    assert 'ELF32' in header and 'big endian' in header and 'PowerPC' in header, name
    assert '[' + soname + ']' in dynamic, (name, soname)
    assert '(RPATH)' not in dynamic and '(RUNPATH)' not in dynamic, name
    shutil.copy2(lib, runtime / name)
    checked[name] = {'soname': soname, 'sha256': sha(lib),
                     'needed': re.findall(r'\(NEEDED\).*\[(.+)\]', dynamic)}
(source / 'runtime-files.sha256').write_text(
    ''.join(f"{v['sha256']}  runtime/{k}\n" for k, v in checked.items()))
(source / 'debian/changelog').write_text(
    f'tabor-gcc14-runtime ({a.version}) tabor-trixie; urgency=medium\n\n'
    '  * GCC 14.2 SPE target runtimes from scripts/build-gcc14-spe-sdk.sh.\n\n'
    ' -- Tabor lab <root@localhost>  Sun, 16 Nov 2026 00:00:00 +0000\n')
(source / 'debian/copyright').write_text(
    'GCC 14.2 runtime libraries, Free Software Foundation copyright holders.\n'
    'GPL-3.0-or-later with GCC Runtime Library Exception 3.1; notices preserved in COPYING.RUNTIME.\n\n'
    + (a.gcc_source / 'COPYING.RUNTIME').read_text())
log = (a.output / 'build.log').open('w')
subprocess.run(['dpkg-buildpackage', '-a', 'powerpcspe', '-B', '-us', '-uc'], cwd=source,
               stdout=log, stderr=subprocess.STDOUT, check=True)
packages = {}
for deb in sorted(a.output.glob('*.deb')):
    fields = {f: subprocess.check_output(['dpkg-deb', '-f', str(deb), f], text=True).strip()
              for f in ['Package', 'Architecture', 'Provides', 'Depends']}
    assert fields['Architecture'] == 'powerpcspe', fields
    packages[deb.name] = {'sha256': sha(deb), **fields}
assert len(packages) == 3, packages
(a.output / 'receipt.json').write_text(json.dumps({
    'status': 'target-runtime-packages-built-not-installed', 'version': a.version,
    'recipe_sha256': sha(Path(__file__)), 'libraries': checked, 'packages': packages}, indent=2) + '\n')
print('\n'.join(packages))
