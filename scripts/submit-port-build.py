#!/usr/bin/env python3
"""Freeze the reviewed port inputs and launch one bounded R730 pipeline."""
import argparse
import io
import json
import re
import shlex
import subprocess
import tarfile
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--run-id', required=True)
p.add_argument('--native-audit', required=True, help='Existing verified R730 work/... audit')
p.add_argument('--plan',default='profiles/sbuild/ready-core-batch.json',help='Reviewed pipeline plan within the project')
p.add_argument('--after-run',help='Queue this reviewed round after an existing pipeline; never overlap its workers')
a = p.parse_args()
assert re.fullmatch(r'[a-z0-9-]+', a.run_id)
assert re.fullmatch(r'profiles/sbuild/[a-z0-9-]+\.json',a.plan)
assert re.fullmatch(r'work/[a-z0-9-]+', a.native_audit)
if a.after_run:assert re.fullmatch(r'[a-z0-9-]+',a.after_run)
project = Path(__file__).resolve().parents[1]
helper = project.parent / 'lab/consolidation-20261002/r730-prep-20261031'
base = '/srv/data1/tabor-build/linux-live-001'

def remote(args, root=False, **kwargs):
    return subprocess.run(['python3', str(helper / ('sudo.py' if root else 'remote.py')),
                           shlex.join(list(map(str, args)))], check=True, **kwargs)

submission_unit = 'tabor-port-pipeline-next' if a.after_run else 'tabor-port-pipeline'
for unit in ['tabor-port-pipeline', 'tabor-port-pipeline-next', 'tabor-ready-batch', 'tabor-indep-batch',
             'tabor-sbuild-proof', 'tabor-xorgproto-proof']:
    check = subprocess.run(['python3', str(helper / 'remote.py'),
        shlex.join(['systemctl', 'is-active', '--quiet', unit])], capture_output=True)
    if check.returncode==0 and a.after_run and unit in ['tabor-port-pipeline','tabor-port-pipeline-next']:
        expected=base+'/work/'+a.after_run
        command=subprocess.check_output(['python3',str(helper/'remote.py'),shlex.join(['systemctl','show','--value','--property=ExecStart',unit])],text=True)
        assert re.search(r'--output '+re.escape(expected)+r'(?=[ ;}]|$)',command),'Active pipeline differs from the requested predecessor (an after-receipt reference is not its output)'
        submission_unit = 'tabor-port-pipeline-next' if unit=='tabor-port-pipeline' else 'tabor-port-pipeline'
    else:assert check.returncode != 0, 'Existing package controller/job: ' + unit
snapshot = base + '/submissions/' + a.run_id + '/project'
remote(['python3', '-c', 'from pathlib import Path;Path(' + repr(snapshot) + ').mkdir(parents=True,exist_ok=False)'])
payload = io.BytesIO()
defaults = json.loads((project / 'profiles/sbuild/libx11.json').read_text())
paths = ['scripts', 'profiles', 'patches', 'packaging', 'bench']
if defaults.get('configure_cache'):
    paths += [x['path'] for x in defaults['configure_cache']['evidence']]
def include(info):
    return None if '__pycache__' in Path(info.name).parts or info.name.endswith('.pyc') else info
with tarfile.open(fileobj=payload, mode='w') as tar:
    for name in paths:
        tar.add(project / name, arcname=name, filter=include)
assert payload.tell() < 32 * 1024 * 1024, 'Unexpectedly large submission; review inputs'
remote(['tar', '-xf', '-', '-C', snapshot], input=payload.getvalue())
command=['systemd-run', '--unit='+submission_unit, '--collect',
    '--property=CPUQuota=100%', '--property=MemoryMax=1G', '--property=TasksMax=128',
    'python3', snapshot + '/scripts/run-port-build.py', '--project', snapshot,
    '--base', base, '--plan', snapshot + '/' + a.plan,
    '--native-audit', base + '/' + a.native_audit,
    '--output', base + '/work/' + a.run_id]
if a.after_run:command.extend(['--after-receipt',base+'/work/'+a.after_run+'/receipt.json'])
remote(command,root=True)
print('Submitted scoped Debian port pipeline:', a.run_id)
