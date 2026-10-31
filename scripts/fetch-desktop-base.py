#!/usr/bin/env python3
"""Fetch only the source files in the reviewed desktop prerequisite lock."""
import argparse,hashlib,json,urllib.request
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--lock',type=Path,required=True);p.add_argument('--cache',type=Path,required=True);a=p.parse_args();a.cache.mkdir(parents=True,exist_ok=True)
for comp in json.loads(a.lock.read_text())['components'].values():
 for f in comp['files']:
  assert Path(f['filename']).name==f['filename'] and f['url'].startswith('https://')
  dest=a.cache/f['filename']
  if not dest.exists():
   data=urllib.request.urlopen(f['url'],timeout=60).read()
   assert len(data)==f['size'] and hashlib.sha256(data).hexdigest()==f['sha256'],f['filename']
   dest.write_bytes(data)
  assert dest.stat().st_size==f['size'] and hashlib.sha256(dest.read_bytes()).hexdigest()==f['sha256'],dest
 print(comp['version'],'source hashes verified')
