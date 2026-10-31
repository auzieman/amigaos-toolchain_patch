#!/usr/bin/env python3
"""Run the isolated OS4 cross-build; perform image/source intake separately."""
import argparse
import json
import re
import subprocess
from pathlib import Path

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--project',type=Path,required=True)
p.add_argument('--softfp',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--image',required=True,help='Repository digest or local derived-image sha256 ID')
p.add_argument('--uid',type=int,default=1000)
p.add_argument('--gid',type=int,default=1000)
a=p.parse_args()
profile=json.loads((a.project/'profiles/amigaos-docker-spe.json').read_text())
image=a.image
if not re.fullmatch(r'(?:[\w./-]+@)?sha256:[0-9a-f]{64}',image):p.error('Image digest required')
for source in [a.project,a.softfp]:
    if not source.is_dir():p.error(f'Missing input directory: {source}')
inspection=json.loads(subprocess.check_output(['docker','image','inspect',image],text=True))[0]
if inspection['Architecture']!='amd64':p.error('Expected linux/amd64 compiler image')
a.output.mkdir(parents=True,exist_ok=False)
command=['docker','run','--rm','--pull=never','--cpus=2','--memory=4g','--network=none',
         '--cap-drop=ALL','--security-opt=no-new-privileges','--read-only',
         '--tmpfs','/tmp:rw,size=512m','--user',f'{a.uid}:{a.gid}',
         '--mount',f'type=bind,src={a.project.resolve()},dst=/project,readonly',
         '--mount',f'type=bind,src={a.softfp.resolve()},dst=/softfp,readonly',
         '--mount',f'type=bind,src={a.output.resolve()},dst=/out',
         '--entrypoint','python3',image,'/project/scripts/amigaos-container-build.py',
         '--image',image]
# Root-managed Docker, ordinary owner-readable artifacts.
import os
if os.geteuid()==0:os.chown(a.output,a.uid,a.gid)
(a.output/'host-run.json').write_text(json.dumps({'image':image,'image_id':inspection['Id'],
    'command':command,'amigaos_execution':False},indent=2)+'\n')
result=subprocess.run(command)
raise SystemExit(result.returncode)
