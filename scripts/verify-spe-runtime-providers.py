#!/usr/bin/env python3
"""Verify real coinstalled SPE runtime providers without executing target code."""
import argparse, hashlib, json, os, subprocess, tarfile
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for name in ['project','canonical-receipt','provider-receipt','output']:
    p.add_argument('--'+name,type=Path,required=True)
a=p.parse_args()
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
canonical=json.loads(a.canonical_receipt.read_text());providers=json.loads(a.provider_receipt.read_text())
assert canonical['status']==providers['status']=='debian-packages-built-not-target-installed'
assert providers['build_root_only'] and not canonical.get('build_root_only')
assert canonical['input_libraries']==providers['input_libraries']
names={'libgcc_s.so.1','libstdc++.so.6.0.25'}
def packaged(receipt,record):
    found={}
    for filename,item in record['packages'].items():
        f=receipt.parent/filename;assert sha(f)==item['sha256']
        proc=subprocess.Popen(['dpkg-deb','--fsys-tarfile',str(f)],stdout=subprocess.PIPE)
        with tarfile.open(fileobj=proc.stdout,mode='r|') as tar:
            for member in tar:
                name=Path(member.name).name
                if not member.isfile() or name not in names:continue
                data=tar.extractfile(member).read()
                assert data[:6]==b'\x7fELF\x01\x02' and int.from_bytes(data[18:20],'big')==20
                assert name not in found
                found[name]=hashlib.sha256(data).hexdigest()
        assert proc.wait()==0
    assert set(found)==names
    return found
original=packaged(a.canonical_receipt,canonical);alternate=packaged(a.provider_receipt,providers)
assert original==alternate,'Normal debhelper runtime payload differs from canonical packages'
for name,digest in original.items():
    assert sha(Path('/usr/lib/powerpc-linux-gnuspe')/name)==digest
subprocess.run(['python3',a.project/'scripts/verify-spe-managed-toolchain.py',
                '--output',a.output],check=True)
env={**os.environ,'CC':'/usr/lib/tabor-spe-toolchain/bin/powerpc-linux-gnuspe-gcc'}
deps=subprocess.check_output(['dpkg-architecture','-apowerpcspe','-c',
    'dpkg-shlibdeps -O -e'+str(a.output/'probe-cc')],cwd=a.project/'packaging/gcc-runtime',env=env,text=True)
assert all(s in deps for s in ['libgcc-s1','libstdc++6']) and 'tabor-spe-' not in deps
state=subprocess.check_output(['dpkg-query','-W',
    '-f=${binary:Package}\t${Version}\t${Architecture}\t${db:Status-Status}\t${Provides}\n',
    'libgcc-s1:amd64','libstdc++6:amd64','tabor-spe-libgcc-s1:powerpcspe',
    'tabor-spe-libstdc++6:powerpcspe','libgmp-dev:powerpcspe','libgmpxx4ldbl:powerpcspe'],text=True)
assert subprocess.check_output(['dpkg','--audit'],text=True)==''
(a.output/'package-state.json').write_text(json.dumps({
    'status':'real-runtime-providers-gmp-install-and-dependency-generation-passed',
    'recipe_sha256':sha(Path(__file__)),'target_execution':False,
    'canonical_receipt_sha256':sha(a.canonical_receipt),
    'provider_receipt_sha256':sha(a.provider_receipt),'installed':state,
    'canonical_dependencies':deps,'raw_compiler_runtime_sha256':canonical['input_libraries'],
    'packaged_runtime_sha256':original,
    'payload_note':'Compare canonical/provider packages after normal debhelper stripping, then installed bytes'},indent=2)+'\n')
