#!/usr/bin/env python3
"""Fresh, hash-locked Debian binary package build against the SPE sysroot.

Uses Debian debian/rules and generated maintainer metadata. Package installation
belongs to the pinned build image; compilation never fabricates installed state.
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
p.add_argument('--indep-only', action='store_true', help='Build Architecture: all scripting/data packages with Debian -A semantics')
p.add_argument('--check-dependencies-only', action='store_true', help='Fresh source preflight using Debian dependency semantics; do not compile')
p.add_argument('--preserve-debian-version', action='store_true',
               help='Keep the pinned Debian changelog/version for normal build-root coinstallation; provenance remains in receipts')
p.add_argument('--package-managed-root', action='store_true',
               help='Use installed target development packages, without bootstrap shlibs/sysroot transport overrides')
p.add_argument('--binary-nmu', type=int, default=0, help='Reviewed Debian binary-only rebuild number; uses Debian source-changelog writer, not binary metadata rewriting')
a = p.parse_args()
assert 0 <= a.binary_nmu <= 9
if a.binary_nmu:
    assert a.preserve_debian_version and a.arch_only and not a.indep_only
if a.package_managed_root:
    assert a.sysroot == Path('/'), 'Package-managed build uses the container root'
assert not (a.arch_only and a.indep_only)
assert __import__('re').fullmatch(r'[a-z0-9,-]*', a.build_profiles)
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
           DEB_BUILD_OPTIONS=('nocheck ' if 'nocheck' in a.build_profiles.split(',') else '') + 'parallel=' + str(a.jobs),
           DEB_BUILD_PROFILES=a.build_profiles.replace(',', ' '), LC_ALL='C.UTF-8',
           TABOR_SYSROOT=str(a.sysroot),
           TABOR_SHLIBS=str(a.project / 'profiles/images/spe-bootstrap.shlibs'))
if a.package_managed_root:
    # Debian packages may legitimately replace MAINT_APPEND. Architecture and
    # installed-root defaults therefore belong to the compiler, not CFLAGS.
    for name in ['TABOR_SYSROOT', 'TABOR_SHLIBS', 'DEB_CFLAGS_MAINT_APPEND',
                 'DEB_CXXFLAGS_MAINT_APPEND', 'DEB_LDFLAGS_MAINT_APPEND']:
        env.pop(name, None)
    observed_root = subprocess.check_output([str(cc), '-print-sysroot'], text=True).strip()
    assert observed_root == '/', 'Managed builds require a compiler configured for the installed root'
    macros = subprocess.check_output([str(cc), '-dM', '-E', '-'], input='', text=True)
    for required in ['#define __SPE__ 1', '#define __NO_FPRS__ 1',
                     '#define __LONG_DOUBLE_128__ 1', '#define __BYTE_ORDER__ __ORDER_BIG_ENDIAN__']:
        assert required in macros, 'Incorrect default target ABI: ' + required
    # Debian cross rules choose the standard tuple-prefixed tools. An absolute
    # CC is not portable: OpenSSL prepends CROSS_COMPILE to that value.
    env.pop('CC', None)
    env.pop('CXX', None)
    flags = []

if a.indep_only:
    # CC otherwise makes dpkg-architecture infer a cross host even for -A.
    # Pure scripting/data builds use host tools and must only emit Arch: all.
    env['PATH'] = os.environ['PATH']
    for name in ['CC', 'CXX', 'DEB_CFLAGS_MAINT_APPEND', 'DEB_CXXFLAGS_MAINT_APPEND',
                 'DEB_LDFLAGS_MAINT_APPEND', 'TABOR_SYSROOT', 'TABOR_SHLIBS']:
        env.pop(name, None)
r = {'status': 'running', 'package': a.package, 'source_version': component['version'],
     'build_profiles': a.build_profiles, 'arch_only': a.arch_only, 'indep_only': a.indep_only,
     'dependency_preflight_only': a.check_dependencies_only,
     'preserve_debian_version': a.preserve_debian_version,
     'package_managed_root': a.package_managed_root,
     'image_id': a.image_id, 'recipe_sha256': sha(Path(__file__)),
     'source_lock_sha256': sha(lockpath), 'compiler_sha256': sha(cc),
     'compiler_frontend_sha256': sha(frontend),
     'sysroot_libraries': {str(f.relative_to(a.sysroot)): sha(f)
         for f in sorted((a.sysroot / 'lib').glob('*.so*')) if f.is_file()},
     'flags': [] if a.indep_only else flags,
     'bootstrap_shlibs_sha256': sha(Path(env['TABOR_SHLIBS'])) if 'TABOR_SHLIBS' in env else None,
     'compiler_used': not a.indep_only, 'commands': [], 'target_tests': 'pending',
     'package_installation': 'not-attempted', 'physical_boot': False}
submission = a.project / 'submission.json'
if submission.exists():
    r['submission_sha256'] = sha(submission)
    manifest = json.loads(submission.read_text())
    for name, digest in manifest['files'].items():
        candidate = a.project / name
        assert candidate.resolve().is_relative_to(a.project.resolve())
        assert sha(candidate) == digest, 'Submitted build input changed: ' + name
if a.package_managed_root:
    installed = subprocess.check_output(['dpkg-query', '-W',
        '-f=${binary:Package}\t${Version}\t${Architecture}\t${db:Status-Status}\n'], text=True)
    r['installed_target_packages'] = [line for line in installed.splitlines()
        if '\tpowerpcspe\tinstalled' in line]
    assert r['installed_target_packages'], 'Managed root has no configured target packages'
    r['sysroot_libraries'] = {str(f.relative_to(a.sysroot)): sha(f)
        for f in sorted((a.sysroot / 'usr/lib/powerpc-linux-gnuspe').glob('*.so*')) if f.is_file()}
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
        original_version = subprocess.check_output(['dpkg-parsechangelog', '-l', str(changelog), '-SVersion'], text=True).strip()
        assert original_version == component['version'], 'Pinned source version disagrees with Debian changelog'
        r['original_debian_changelog_sha256'] = sha(changelog)
        version = component['version'] + '+tabor1'
        if 'stage2' in a.build_profiles.split(','):
            version += '~stage2'
        if a.preserve_debian_version:
            # Multi-Arch: same libraries must share Debian's exact version and
            # common documentation with the installed native build tools.
            # Keep upstream changelog bytes; patch identity lives in receipts.
            version = component['version']
        else:
            changelog.write_text(f'{a.package} ({version}) tabor-trixie; urgency=medium\n\n'
                '  * Rebuild for the experimental Tabor SPE sysroot.\n\n'
                ' -- Tabor lab <root@localhost>  Sun, 01 Nov 2026 16:00:00 +0000\n\n'
                + changelog.read_text())
        if a.binary_nmu:
            # One binary-only stanza is essential: repeated dch --bin-nmu
            # calls leave intermediate entries in shared changelog files.
            # Debian's writer formats the entry; preserve upstream bytes below.
            from debian.changelog import Changelog
            from email.utils import formatdate
            original_bytes = changelog.read_bytes()
            upstream = Changelog(original_bytes.decode('utf-8'), strict=True)
            version = component['version'] + '+b' + str(a.binary_nmu)
            entry = Changelog()
            entry.new_block(package=upstream.package, version=version,
                distributions='trixie', urgency='medium', other_pairs={'binary-only': 'yes'},
                author='Tabor lab <root@localhost>', date=formatdate(localtime=False))
            entry.add_change('')
            entry.add_change('  * Binary-only cross-build for powerpcspe; no source changes.')
            entry.add_change('')
            changelog.write_bytes((str(entry).rstrip('\n') + '\n\n').encode('utf-8') + original_bytes)
            parsed = list(Changelog(changelog.read_text(), strict=True))
            assert str(parsed[0].version) == version
            assert str(parsed[1].version) == component['version'], 'Binary rebuild stanza lost the original source header'
            observed = subprocess.check_output(['dpkg-parsechangelog', '-l', str(changelog), '-SVersion'], text=True).strip()
            assert observed == version
            r['binary_nmu'] = a.binary_nmu
            r['binary_nmu_writer'] = 'python-debian Changelog; one binary-only stanza'
            r['binary_nmu_changelog_sha256'] = sha(changelog)
        r['binary_version'] = version
        if a.package == 'glibc':
            # Debian generates its control from architecture-specific templates.
            env['LINUX_SOURCE'] = str(a.sysroot / 'usr')
            run(['dpkg-architecture', '-apowerpcspe', '-c',
                 'make -f debian/rules debian/control'], source)
        if a.check_dependencies_only:
            command = ['dpkg-checkbuilddeps']
            if a.build_profiles:
                command += ['-P', a.build_profiles]
            if a.indep_only:
                command.append('-A')
            else:
                command += ['-a', 'powerpcspe']
            if a.arch_only:
                command.append('-B')
            r['active_phase'] = 'debian-build-dependency-preflight'
            run(command, source)
            r['status'] = 'build-dependencies-satisfied-not-built'
        else:
            command = ['dpkg-buildpackage']
            if a.indep_only:
                command.append('-A')
            else:
                command += ['-a', 'powerpcspe', '-B' if a.arch_only else '-b']
            run(command + ['-us', '-uc'], source)
            packages = {}
            for deb in sorted([*a.work.glob('*.deb'), *a.work.glob('*.udeb')]):
                metadata = subprocess.check_output(['dpkg-deb', '-f', str(deb), 'Architecture'], text=True).strip()
                assert metadata in ['powerpcspe', 'all'], metadata
                if a.indep_only:
                    assert metadata == 'all', 'Independent build produced an architecture-specific package'
                packages[deb.name] = {'sha256': sha(deb), 'bytes': deb.stat().st_size,
                                      'architecture': metadata}
            assert packages, 'No Debian binary packages generated'
            r['packages'] = packages
            if a.package == 'glibc':
                script = source / 'debian/libc6-dev/usr/lib/powerpc-linux-gnuspe/libc.so'
                assert 'OUTPUT_FORMAT(elf32-powerpc)' in script.read_text(), 'SPE libc linker script has the wrong BFD format; check cross OBJDUMP selection'
                r['libc_linker_script'] = {'sha256': sha(script), 'format': 'elf32-powerpc'}
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
