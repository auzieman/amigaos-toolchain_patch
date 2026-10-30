#!/usr/bin/env python3
"""Populate the immutable Debian archive cache from the reviewed lock."""
from pathlib import Path
import hashlib,json,urllib.request
root=Path(__file__).resolve().parents[1]
cache=root/'downloads/debian';cache.mkdir(parents=True,exist_ok=True)
lock=json.loads((root/'profiles/debian-trixie.lock.json').read_text())
for component in lock['components'].values():
 for f in component['files']:
  path=cache/f['filename']
  if Path(f['filename']).name!=f['filename']:raise SystemExit('Invalid cache name')
  if not path.exists():
   tmp=path.with_name(path.name+'.partial')
   with urllib.request.urlopen(f['url'],timeout=60) as src,tmp.open('wb') as dst:
    while chunk:=src.read(1024*1024):dst.write(chunk)
   if tmp.stat().st_size!=f['size'] or hashlib.sha256(tmp.read_bytes()).hexdigest()!=f['sha256']:
    raise SystemExit('Download mismatch: '+f['filename'])
   tmp.rename(path)
  if path.stat().st_size!=f['size'] or hashlib.sha256(path.read_bytes()).hexdigest()!=f['sha256']:
   raise SystemExit('Cached input mismatch: '+f['filename'])
  print('Verified',f['filename'])
