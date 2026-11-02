#!/usr/bin/env python3
"""Debhelper package assembly of already compiled, provenance-checked SPE runtimes.

Does not rebuild a compiler or execute a target program. This is an explicit
bootstrap assembly stage, not a fresh Debian GCC source-package build.
"""
import argparse, hashlib, json, os, shutil, subprocess, tarfile
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
for n in ['project', 'tools', 'cache', 'compiler-receipt', 'sysroot', 'output']:
    p.add_argument('--' + n, type=Path, required=True)
p.add_argument('--image-id', required=True)
a = p.parse_args(); a.output.mkdir(exist_ok=False)
sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
spec = json.loads((a.project / 'profiles/toolchain-bootstrap.json').read_text())
original = json.loads(a.compiler_receipt.read_text())
assert original['status'] == 'reference-cxx-runtime-built-not-executed'
assert original['source_sha512'] == spec['gcc']['sha512']
assert original['target'] == spec['target'] == 'powerpc-linux-gnuspe'
assert '-mlong-double-128' in original['target_runtime_flags']
for patch in original.get('patches', []):
    assert sha(a.project / patch['path']) == patch['sha256']
archive = a.cache / spec['gcc']['filename']
with archive.open('rb') as f:
    assert hashlib.file_digest(f, 'sha512').hexdigest() == spec['gcc']['sha512']
# Same tree identity recorded by bootstrap-spe-compiler.py, without target execution.
h = hashlib.sha256()
for f in sorted(a.tools.rglob('*')):
    if f.is_symlink(): value = 'link:' + os.readlink(f)
    elif f.is_file(): value = sha(f)
    else: continue
    h.update((str(f.relative_to(a.tools)) + '\0' + value + '\n').encode())
assert h.hexdigest() == original['installed_tree_sha256'], 'Recorded compiler/runtime tree changed'
source = a.output / 'source'; source.mkdir()
shutil.copytree(a.project / 'packaging/gcc-runtime/debian', source / 'debian')
(source / 'debian/rules').chmod(0o755)
runtime = source / 'runtime'; runtime.mkdir()
inputs = {}
for name, soname in [('libgcc_s.so.1', 'libgcc_s.so.1'), ('libstdc++.so.6.0.25', 'libstdc++.so.6')]:
    f = a.tools / spec['target'] / 'lib' / name
    header = subprocess.check_output(['readelf', '-h', str(f)], text=True)
    dynamic = subprocess.check_output(['readelf', '-d', str(f)], text=True)
    assert 'ELF32' in header and 'big endian' in header and 'PowerPC' in header
    assert '[' + soname + ']' in dynamic
    assert '(RPATH)' not in dynamic and '(RUNPATH)' not in dynamic
    shutil.copyfile(f, runtime / name); inputs[name] = sha(f)
(source / 'runtime-files.sha256').write_text(''.join(digest + '  runtime/' + name + '\n' for name,digest in inputs.items()))
version = '8.5.0+tabor1'
(source / 'debian/changelog').write_text(f'''tabor-gcc-runtime ({version}) tabor-trixie; urgency=medium

  * Assemble real target runtimes from the recorded patched GCC compilation.

 -- Tabor lab <root@localhost>  Mon, 02 Nov 2026 12:00:00 +0000
''')
licenses = source / 'licenses'; licenses.mkdir()
with tarfile.open(archive) as tar:
    for name in ['COPYING3', 'COPYING3.LIB', 'COPYING.RUNTIME']:
        (licenses / name).write_bytes(tar.extractfile('gcc-8.5.0/' + name).read())
(licenses / 'compiler-build-receipt.json').write_text(json.dumps(original, indent=2) + '\n')
(licenses / 'provenance.json').write_text(json.dumps({'source': spec['gcc'], 'inputs': inputs,
    'phase': 'assembly of recorded cross-compiled runtimes; no target execution'}, indent=2) + '\n')
for item in original.get('patches', []):
    dest = licenses / 'patches' / Path(item['path']).name
    dest.parent.mkdir(exist_ok=True); shutil.copyfile(a.project / item['path'], dest)
(source / 'debian/copyright').write_text('GCC 8.5 runtime libraries, Free Software Foundation copyright holders.\nGPL-3.0-or-later with GCC Runtime Library Exception 3.1; upstream notices preserved in attached license files.\nSource: ' + spec['gcc']['url'] + '\n')
for name in ['libgcc-s1', 'libstdc++6']:
    (source / ('debian/' + name + '.docs')).write_text('licenses/*\n')
r = {'status': 'running', 'package': 'tabor-gcc-runtime', 'image_id': a.image_id,
     'source_version': '8.5.0', 'binary_version': version, 'recipe_sha256': sha(Path(__file__)),
     'compiler_receipt_sha256': sha(a.compiler_receipt), 'source_sha512': spec['gcc']['sha512'],
     'input_libraries': inputs, 'build_phase': 'assembly-of-existing-recorded-target-compilation',
     'libc_header_sha256': sha(a.sysroot / 'usr/include/unistd.h'),
     'target_execution': False, 'package_installation': 'not-attempted', 'packages': {}}
try:
    env = {**os.environ, 'PATH': str(a.tools / 'bin') + ':' + os.environ['PATH'], 'LC_ALL': 'C.UTF-8'}
    env['CC'] = str(a.tools / 'bin/powerpc-linux-gnuspe-gcc') + ' --sysroot=' + str(a.sysroot)
    with (a.output / 'build.log').open('w') as log:
        subprocess.run(['dpkg-buildpackage', '-a', 'powerpcspe', '-B', '-us', '-uc'],
                       cwd=source, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
    for f in sorted(a.output.glob('*.deb')):
        arch = subprocess.check_output(['dpkg-deb', '-f', str(f), 'Architecture'], text=True).strip()
        assert arch == 'powerpcspe'
        r['packages'][f.name] = {'sha256': sha(f), 'bytes': f.stat().st_size, 'architecture': arch}
    assert any(n.startswith('libgcc-s1_') for n in r['packages'])
    assert any(n.startswith('libstdc++6_') for n in r['packages'])
    r['status'] = 'debian-packages-built-not-target-installed'
except Exception as e:
    r.update(status='failed', error=str(e)); raise
finally:
    (a.output / 'receipt.json').write_text(json.dumps(r, indent=2) + '\n')
print(r['status'])
