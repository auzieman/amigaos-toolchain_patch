#!/usr/bin/env python3
"""Hash-check package receipts and inspect ELF payload headers without execution."""
import argparse, hashlib, json, subprocess, tarfile
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--receipt',nargs='+',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
r={'status':'running','recipe_sha256':sha(Path(__file__)),'target_execution':False,'sources':[]}
for receipt in a.receipt:
    record=json.loads(receipt.read_text())
    assert record['status']=='debian-packages-built-not-target-installed'
    source={'receipt':str(receipt),'receipt_sha256':sha(receipt),'packages':[]}
    for filename,entry in record['packages'].items():
        assert Path(filename).name==filename
        package=receipt.parent/filename;assert sha(package)==entry['sha256']
        arch=subprocess.check_output(['dpkg-deb','-f',str(package),'Architecture'],text=True).strip()
        assert arch in ['powerpcspe','all']
        payload={'file':filename,'sha256':entry['sha256'],'architecture':arch,'elf_files':[]}
        proc=subprocess.Popen(['dpkg-deb','--fsys-tarfile',str(package)],stdout=subprocess.PIPE)
        with tarfile.open(fileobj=proc.stdout,mode='r|') as tar:
            for member in tar:
                if not member.isfile():continue
                header=tar.extractfile(member).read(20)
                if header[:4]!=b'\x7fELF':continue
                assert arch=='powerpcspe','Independent package contains ELF: '+filename
                assert header[4:6]==bytes([1,2]) and int.from_bytes(header[18:20],'big')==20,(filename,member.name,header.hex())
                payload['elf_files'].append(member.name)
        assert proc.wait()==0
        source['packages'].append(payload)
    r['sources'].append(source)
r['status']='package-hashes-and-elf32-big-endian-powerpc-payloads-verified'
r['source_count']=len(r['sources'])
r['package_count']=sum(len(s['packages']) for s in r['sources'])
r['elf_count']=sum(len(p['elf_files']) for s in r['sources'] for p in s['packages'])
with a.output.open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:r[k] for k in ['status','source_count','package_count','elf_count','target_execution']}))
