#!/usr/bin/env python3
"""Exercise backend discovery and selected-Go checks using the packaged helper.

Runs only native Perl/Go host tools in a read-only native template. No target
code executes and no package database is edited.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
for name in ['root', 'receipt', 'output']:
    p.add_argument('--' + name, type=Path, required=True)
a = p.parse_args()
a.output.mkdir(exist_ok=False)
record = json.loads(a.receipt.read_text())
assert record['status'] == 'debian-packages-built-not-target-installed'
name = next(n for n in record['packages'] if n.startswith('dh-golang_') and n.endswith('_all.deb'))
package = a.receipt.parent / name
assert hashlib.sha256(package.read_bytes()).hexdigest() == record['packages'][name]['sha256']
subprocess.run(['dpkg-deb', '-x', str(package), str(a.output / 'payload')], check=True)
fixture = a.output / 'fixture'
(fixture / 'debian').mkdir(parents=True)
(fixture / 'debian/control').write_text('Source: backend-probe\nBuild-Depends: debhelper-compat (= 13)\nXS-Go-Import-Path: example.test/backend-probe\n\nPackage: backend-probe\nArchitecture: any\nDescription: Native helper regression fixture\n')
probe = a.output / 'probe.pl'
probe.write_text('''use strict;
use Debian::Debhelper::Buildsystem::golang;
chdir('/mnt/fixture') or die $!;
my $backend = Debian::Debhelper::Buildsystem::golang->new();
if ($ARGV[0] eq 'discover') {
    die "C source selected Go backend" if $backend->check_auto_buildable();
} else {
    $backend->pre_building_step('configure');
}
print "HOST_HELPER_PROBE_PASS\\n";
''')
tests = [('original-c-spe', False, 'powerpcspe', 'discover', False),
         ('patched-c-spe', True, 'powerpcspe', 'discover', True),
         ('patched-go-spe', True, 'powerpcspe', 'selected', False),
         ('patched-go-native', True, 'amd64', 'selected', True)]
r = {'status': 'running', 'target_execution': False, 'native_regression': True, 'items': []}
try:
    for label, patched, host, mode, success in tests:
        cmd = ['systemd-nspawn', '--quiet', '--register=no', '--timezone=off', '--read-only',
               '--directory=' + str(a.root), '--bind=' + str(a.output) + ':/mnt',
               '--setenv=DEB_BUILD_ARCH=amd64', '--setenv=DEB_HOST_ARCH=' + host]
        if patched:
            cmd.append('--setenv=PERL5LIB=/mnt/payload/usr/share/perl5')
        cmd += ['/usr/bin/dpkg-architecture', '-a' + host, '-c', '/usr/bin/perl /mnt/probe.pl ' + mode]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        (a.output / (label + '.log')).write_text(result.stdout)
        if success:
            assert result.returncode == 0 and 'HOST_HELPER_PROBE_PASS' in result.stdout, result.stdout
        else:
            assert result.returncode != 0 and 'Missing entry for CPU/ABI powerpc/spe' in result.stdout, result.stdout
        r['items'].append({'test': label, 'exit': result.returncode, 'expected_success': success})
    r['status'] = 'native-helper-regression-passed'
except Exception as error:
    r.update(status='failed', error=str(error))
    raise
finally:
    (a.output / 'receipt.json').write_text(json.dumps(r, indent=2) + '\n')
