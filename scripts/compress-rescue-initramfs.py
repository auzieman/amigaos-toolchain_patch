#!/usr/bin/env python3
"""Compress a complete, receipt-verified initramfs and verify its round-trip."""
import argparse,gzip,hashlib,json,shutil
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,required=True);a=p.parse_args();b=a.input;r=json.loads((b/'receipt.json').read_text());assert r['status']=='rescue-initramfs-extended'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();raw=b/'shell.cpio';assert sha(raw)==r['initramfs_sha256'];out=b/'shell.cpio.gz';assert not out.exists()
with raw.open('rb') as src,out.open('xb') as dst:
 with gzip.GzipFile(filename='',mode='wb',fileobj=dst,mtime=0,compresslevel=6) as gz:shutil.copyfileobj(src,gz)
h=hashlib.sha256()
with gzip.open(out,'rb') as f:
 while chunk:=f.read(1024**2):h.update(chunk)
assert h.hexdigest()==r['initramfs_sha256']
(b/'gzip-receipt.json').write_text(json.dumps({'status':'rescue-initramfs-compressed','raw_receipt_sha256':sha(b/'receipt.json'),'raw_initramfs_sha256':r['initramfs_sha256'],'initramfs_sha256':sha(out),'bytes':out.stat().st_size,'physical_boot':False},indent=2)+'\n')
print('Verified compressed initramfs bytes',out.stat().st_size)
