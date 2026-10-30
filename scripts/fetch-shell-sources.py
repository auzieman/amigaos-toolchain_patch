#!/usr/bin/env python3
"""Cache the pinned bootstrap compiler and shell archives without modifying sources."""
import argparse,hashlib,json,urllib.request
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--profile',type=Path,default=Path(__file__).resolve().parents[1]/'profiles/toolchain-bootstrap.json')
p.add_argument('--cache',type=Path,required=True)
a=p.parse_args();a.cache.mkdir(parents=True,exist_ok=True)
for component in ['gcc','busybox']:
 spec=json.loads(a.profile.read_text())[component];algorithm='sha512' if 'sha512' in spec else 'sha256'
 target=a.cache/spec['filename']
 def digest(path):
  h=hashlib.new(algorithm)
  with path.open('rb') as f:
   while chunk:=f.read(1024*1024):h.update(chunk)
  return h.hexdigest()
 if target.exists():
  if digest(target)!=spec[algorithm]:raise SystemExit('Cached source mismatch: '+str(target))
 else:
  partial=target.with_suffix(target.suffix+'.partial')
  with urllib.request.urlopen(spec['url'],timeout=60) as src,partial.open('wb') as dst:
   while chunk:=src.read(1024*1024):dst.write(chunk)
  if digest(partial)!=spec[algorithm]:raise SystemExit('Downloaded source mismatch: '+str(partial))
  partial.rename(target)
 print(component,'verified',target)
