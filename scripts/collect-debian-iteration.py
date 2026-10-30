#!/usr/bin/env python3
"""Collect BKC iteration artifacts and verify the returned file hashes."""
from pathlib import Path
import hashlib,io,re,subprocess,sys,tarfile
r=Path(__file__).resolve().parents[1];run=sys.argv[1]
if not re.fullmatch('[a-f0-9-]+',run):raise SystemExit('Invalid run ID')
out=r/'work/results'/run;out.mkdir(parents=True,exist_ok=False)
ssh=['ssh','-i','/home/auzieman/Projects/BlackKnightController/keys/bkc_id_rsa','-o','BatchMode=yes','root@192.168.1.15']
remote='/app/runtime/pipelines/tabor-debian-iteration/artifacts/'+run+'/iteration-results.tgz'
data=subprocess.check_output(ssh+['docker exec c22f6618ad75 cat '+remote],timeout=90)
(out/'iteration-results.tgz').write_bytes(data)
with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as t:t.extractall(out,filter='data')
manifest=out/'SHA256SUMS'
if manifest.exists():
 for line in manifest.read_text().splitlines():
  expected,name=line.split(maxsplit=1);path=(out/name).resolve()
  if not path.is_relative_to(out.resolve()):raise SystemExit('Artifact path escape')
  if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise SystemExit('Artifact hash mismatch: '+name)
 print('Returned artifact hashes pass')
else:print('Run stopped before final artifact hashing; retained partial diagnostics')
print(out)
