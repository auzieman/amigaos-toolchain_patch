#!/usr/bin/env python3
"""Fresh, hash-locked Debian binary package build against the SPE sysroot.

Uses Debian debian/rules and generated maintainer metadata. Never installs
foreign packages on the builder or marks an extracted stage as configured.
"""
import argparse, hashlib, json, os, subprocess
from pathlib import Path
p = argparse.ArgumentParser(description=__doc__)
for name in ['project', 'cache', 'tools', 'sysroot', 'work']:
    p.add_argument('--' + name, type=Path, required=True)
p.add_argument('--source-lock', default='profiles/package-tools.lock.json')
p.add_argument('--package', required=True)
p.add_argument('--image-id', required=True)
p.add_argument('--jobs', type=int, default=4)
p.add_argument('--build-profiles', default='cross,nocheck')
p.add_argument('--arch-only', action='store_true')
p.add_argument('--check-dependencies-only', action='store_true', help='Fresh source preflight using Debian dependency semantics; do not compile')
a = p.parse_args()
assert __import__('re').fullmatch(r'[a-z0-9,-]+', a.build_profiles)
assert 1 <= a.jobs <= 4
assert a.image_id.startswith('sha256:') and len(a.image_id) == 71
a.work.mkdir(parents=True, exist_ok=False)
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
lockpath = a.project / a.source_lock
component = json.loads(lockpath.read_text())['components'][a.package]
cc = a.tools / 'bin/powerpc-linux-gnuspe-gcc'
frontend = Path(subprocess.check_output([str(cc), '-print-prog-name=cc1'], text=True).strip()).resolve()
assert frontend.is_relative_to(a.tools.resolve()), 'Compiler frontend outside selected toolchain'
flags = ['--sysroot=' + str(a.sysroot), '-mcpu=8548', '-mabi=spe', '-mspe',
         '-mfloat-gprs=double', '-mlong-double-128']
env = os.environ.copy()
env.update(PATH=str(a.tools / 'bin') + ':' + env['PATH'], CC=str(cc),
           CXX=str(a.tools / 'bin/powerpc-linux-gnuspe-g++'),
           DEB_CFLAGS_MAINT_APPEND=' '.join(flags),
           DEB_CXXFLAGS_MAINT_APPEND=' '.join(flags),
           DEB_LDFLAGS_MAINT_APPEND=flags[0],
           DEB_BUILD_OPTIONS='nocheck parallel=' + str(a.jobs),
           DEB_BUILD_PROFILES=a.build_profiles.replace(',', ' '), LC_ALL='C.UTF-8',
           TABOR_SYSROOT=str(a.sysroot),
           TABOR_SHLIBS=str(a.project / 'profiles/images/spe-bootstrap.shlibs'))
r = {'status': 'running', 'package': a.package, 'source_version': component['version'],
     'build_profiles': a.build_profiles, 'arch_only': a.arch_only,
     'dependency_preflight_only': a.check_dependencies_only,
     'image_id': a.image_id, 'recipe_sha256': sha(Path(__file__)),
     'source_lock_sha256': sha(lockpath), 'compiler_sha256': sha(cc),
     'compiler_frontend_sha256': sha(frontend),
     'sysroot_libraries': {str(f.relative_to(a.sysroot)): sha(f)
         for f in sorted((a.sysroot / 'lib').glob('*.so*')) if f.is_file()},
     'flags': flags, 'bootstrap_shlibs_sha256': sha(Path(env['TABOR_SHLIBS'])), 'commands': [], 'target_tests': 'pending',
     'package_installation': 'not-attempted', 'physical_boot': False}
def save():
    temporary = a.work / 'receipt.tmp'
    temporary.write_text(json.dumps(r, indent=2) + '\n')
    temporary.replace(a.work / 'receipt.json')
with (a.work / 'build.log').open('w') as log:
    def run(command, cwd):
        command = list(map(str, command)); r['commands'].append(command)
        log.write('$ ' + repr(command) + '\n'); log.flush(); save()
        subprocess.run(command, cwd=cwd, env=env, stdout=log,
                       stderr=subprocess.STDOUT, check=True)
    try:
        for entry in component['files']:
            f = a.cache / entry['filename']
            assert f.stat().st_size == entry['size'] and sha(f) == entry['sha256'], f
        source = a.work / 'source'
        run(['dpkg-source', '--no-check', '-x', a.cache / component['dsc'], source], a.work)
        # All compatibility patches must be explicit, ordered, version- and hash-checked.
        series = a.project / 'patches' / a.package / 'series.json'
        if series.exists():
            patches = json.loads(series.read_text())
            assert patches['version'] == component['version']
            plain = series.with_name('series')
            if plain.exists():
                ordered = [line.split('#', 1)[0].strip() for line in plain.read_text().splitlines()]
                assert [name for name in ordered if name] == [Path(item['path']).name for item in patches['patches']], 'Plain/JSON patch series disagree'
            for item in patches['patches']:
                patch = a.project / item['path']; assert sha(patch) == item['sha256']
                run(['git', 'apply', '--check', patch], source)
                run(['git', 'apply', patch], source)
            r['patch_series_sha256'] = sha(series)
        changelog = source / 'debian/changelog'
        version = component['version'] + '+tabor1'
        if 'stage2' in a.build_profiles.split(','):
            version += '~stage2'
        changelog.write_text(f'{a.package} ({version}) tabor-trixie; urgency=medium\n\n'
            '  * Rebuild for the experimental Tabor SPE sysroot.\n\n'
            ' -- Tabor lab <root@localhost>  Sun, 01 Nov 2026 16:00:00 +0000\n\n'
            + changelog.read_text())
        r['binary_version'] = version
        if a.package == 'glibc':
            # Debian generates its control from architecture-specific templates.
            env['LINUX_SOURCE'] = str(a.sysroot / 'usr')
            run(['dpkg-architecture', '-apowerpcspe', '-c',
                 'make -f debian/rules debian/control'], source)
        if a.check_dependencies_only:
            command = ['dpkg-checkbuilddeps', '-a', 'powerpcspe', '-P', a.build_profiles]
            if a.arch_only:
                command.append('-B')
            r['active_phase'] = 'debian-build-dependency-preflight'
            run(command, source)
            r['status'] = 'build-dependencies-satisfied-not-built'
        else:
            run(['dpkg-buildpackage', '-a', 'powerpcspe',
                 '-B' if a.arch_only else '-b', '-us', '-uc'], source)
            packages = {}
            for deb in sorted([*a.work.glob('*.deb'), *a.work.glob('*.udeb')]):
                metadata = subprocess.check_output(['dpkg-deb', '-f', str(deb), 'Architecture'], text=True).strip()
                assert metadata in ['powerpcspe', 'all'], metadata
                packages[deb.name] = {'sha256': sha(deb), 'bytes': deb.stat().st_size,
                                      'architecture': metadata}
            assert packages, 'No Debian binary packages generated'
            r['packages'] = packages
            r['build_metadata'] = {f.name: sha(f) for pattern in ['*.changes', '*.buildinfo']
                                   for f in sorted(a.work.glob(pattern))}
            r['status'] = 'debian-packages-built-not-target-installed'
    except Exception as error:
        dependency_blocked = (a.check_dependencies_only
            and isinstance(error, subprocess.CalledProcessError)
            and error.cmd[0] == 'dpkg-checkbuilddeps')
        r.update(status='build-dependencies-blocked' if dependency_blocked else 'failed',
                 error=str(error))
        if isinstance(error, subprocess.CalledProcessError):
            r['failed_command_exit'] = error.returncode
        raise
    finally:
        save()
print(r['status'])
