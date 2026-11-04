#!/usr/bin/env python3
"""Reproduce bootstrap manpage mismatch and exercise normal native debhelper.

No target program or maintainer script executes; fixture is packaging input,
not installed package state. Original packages and native root remain unchanged.
"""
import argparse,gzip,hashlib,io,json,subprocess,tarfile
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for n in ['root','receipt','output']:p.add_argument('--'+n,type=Path,required=True)
a=p.parse_args();a.output.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'status':'running','target_execution':False,'receipt_sha256':sha(a.receipt)}
try:
 record=json.loads(a.receipt.read_text());assert record['status']=='debian-packages-built-not-target-installed'
 names=[n for n in record['packages'] if n.startswith('uuid-dev_')];assert len(names)==1
 package=a.receipt.parent/names[0];assert sha(package)==record['packages'][package.name]['sha256']
 fixture=a.output/'fixture';(fixture/'debian').mkdir(parents=True)
 (fixture/'debian/control').write_text('Source: uuid-manpage-probe\nBuild-Depends: debhelper-compat (= 13)\n\nPackage: uuid-dev\nArchitecture: any\nDescription: Native packaging regression fixture\n')
 (fixture/'debian/changelog').write_text('uuid-manpage-probe (1) unstable; urgency=medium\n\n  * Native fixture.\n\n -- Tabor lab <root@localhost>  Wed, 04 Nov 2026 00:00:00 +0000\n')
 data=subprocess.check_output(['dpkg-deb','--fsys-tarfile',str(package)])
 with tarfile.open(fileobj=io.BytesIO(data)) as archive:
  for member in archive:
   if member.isfile() and '/usr/share/man/man3/' in member.name and member.name.endswith('.gz'):
    target=fixture/'debian/uuid-dev/usr/share/man/man3'/Path(member.name).name[:-3]
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(gzip.decompress(archive.extractfile(member).read()))
 alias=fixture/'debian/uuid-dev/usr/share/man/man3/uuid_generate_random.3'
 before=alias.read_bytes();assert before.startswith(b'.so '),'Fixture must reproduce original unexpanded alias'
 command=['systemd-nspawn','--quiet','--register=no','--timezone=off','--read-only',
          '--directory='+str(a.root),'--bind='+str(fixture)+':/mnt','--chdir=/mnt',
          'dh_installman','--language=C']
 with (a.output/'helper.log').open('w') as log:
  assert subprocess.run(command,stdout=log,stderr=subprocess.STDOUT).returncode==0
 expected=gzip.decompress((a.root/'usr/share/man/man3/uuid_generate_random.3.gz').read_bytes())
 after=alias.read_bytes();assert after==expected,'Normal helper did not restore native-compatible content'
 r.update(status='normal-debhelper-manpage-coinstallation-regression-passed',
          package_sha256=sha(package),before_sha256=hashlib.sha256(before).hexdigest(),
          after_sha256=hashlib.sha256(after).hexdigest(),native_expected_sha256=hashlib.sha256(expected).hexdigest(),helper_command=command)
except Exception as error:
 r.update(status='failed',error=str(error));raise
finally:(a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
