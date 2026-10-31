#!/usr/bin/env python3
"""Add manifest-verified files to a built newc rescue archive; never writes media."""
import argparse
import hashlib
import json
import stat
from pathlib import Path, PurePosixPath

p=argparse.ArgumentParser(description=__doc__)
for name in ['base-results','payload','manifest','output']:
    p.add_argument('--'+name,type=Path,required=True)
a=p.parse_args()
sha=lambda b:hashlib.sha256(b).hexdigest()
base=(a.base_results/'shell.cpio').read_bytes()
original=json.loads((a.base_results/'receipt.json').read_text())
assert original['status']=='static-shell-initramfs-built'
assert sha(base)==original['initramfs_sha256']
manifest=json.loads(a.manifest.read_text())
entries={};offset=0
while True:
    start=offset
    assert base[offset:offset+6]==b'070701','Unsupported/truncated cpio'
    fields=[int(base[offset+6+i*8:offset+14+i*8],16) for i in range(13)]
    size,namesize=fields[6],fields[11]
    assert namesize>0
    raw=base[offset+110:offset+110+namesize]
    assert len(raw)==namesize and raw[-1:]==b'\0'
    name=raw[:-1].decode()
    offset=(offset+110+namesize+3)&~3
    assert offset+size<=len(base)
    offset=(offset+size+3)&~3
    if name=='TRAILER!!!':break
    assert name not in entries
    entries[name]=fields[1]
validated=[]
for item in manifest['files']:
    name=item['path'];path=PurePosixPath(name)
    assert not path.is_absolute() and all(x not in ['.','..'] for x in path.parts)
    assert name not in entries and name!='TRAILER!!!'
    source=(a.payload/name).resolve()
    assert source.is_relative_to(a.payload.resolve())
    data=source.read_bytes()
    assert sha(data)==item['sha256'],name
    mode=item.get('mode',0o644)
    assert mode in [0o600,0o644,0o755]
    uid,gid=item.get('uid',0),item.get('gid',0)
    assert uid in [0,74,1000] and gid in [0,74,1000]
    validated.append((name,data,mode,uid,gid))
a.output.mkdir(parents=True,exist_ok=False)
with (a.output/'shell.cpio').open('wb') as out:
    out.write(base[:start])
    def entry(name,mode,data=b'',uid=0,gid=0):
        encoded=name.encode()+b'\0'
        fields=[0,mode,uid,gid,1,0,len(data),0,0,0,0,len(encoded),0]
        header=b'070701'+''.join(f'{v:08x}' for v in fields).encode()
        out.write(header+encoded+b'\0'*(-(len(header)+len(encoded))%4))
        out.write(data+b'\0'*(-len(data)%4))
        entries[name]=mode
    for directory in sorted(manifest.get('directories',[]),key=lambda x:(len(PurePosixPath(x['path']).parts),x['path'])):
        name=directory['path'];path=PurePosixPath(name)
        assert not path.is_absolute() and all(x not in ['.','..'] for x in path.parts)
        assert name not in entries
        for parent in reversed(path.parents):
            ancestor=str(parent)
            if ancestor=='.':continue
            if ancestor not in entries:entry(ancestor,stat.S_IFDIR|0o755)
            assert stat.S_ISDIR(entries[ancestor])
        mode=directory.get('mode',0o755);uid,gid=directory.get('uid',0),directory.get('gid',0)
        assert mode in [0o700,0o755] and uid in [0,74,1000] and gid in [0,74,1000]
        entry(name,stat.S_IFDIR|mode,uid=uid,gid=gid)
    for name,data,mode,uid,gid in sorted(validated):
        for parent in reversed(PurePosixPath(name).parents):
            directory=str(parent)
            if directory=='.':continue
            if directory not in entries:entry(directory,stat.S_IFDIR|0o755)
            assert stat.S_ISDIR(entries[directory]),directory
        assert name not in entries,name
        entry(name,stat.S_IFREG|mode,data,uid,gid)
    entry('TRAILER!!!',0)
receipt={'status':'rescue-initramfs-extended','base_receipt_sha256':sha((a.base_results/'receipt.json').read_bytes()),
         'base_initramfs_sha256':sha(base),'manifest_sha256':sha(a.manifest.read_bytes()),
         'files':manifest['files'],'initramfs_sha256':sha((a.output/'shell.cpio').read_bytes()),
         'initramfs_bytes':(a.output/'shell.cpio').stat().st_size,'physical_boot':False}
(a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
