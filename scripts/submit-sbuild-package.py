#!/usr/bin/env python3
"""Freeze a reviewed sbuild proof specification and start one R730 lab job."""
import argparse,io,json,re,shlex,subprocess,tarfile
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--spec',required=True)
p.add_argument('--run-id',required=True)
a=p.parse_args();project=Path(__file__).resolve().parents[1]
assert re.fullmatch(r'[a-z0-9-]+',a.run_id)
spec=(project/a.spec).resolve();assert spec.is_relative_to(project/'profiles/sbuild')
settings=json.loads(spec.read_text());base='/srv/data1/tabor-build/linux-live-001'
helper=project.parent/'lab/consolidation-20261002/r730-prep-20261031'
def remote(cmd,root=False,**kw):
 return subprocess.run(['python3',str(helper/('sudo.py' if root else 'remote.py')),shlex.join(cmd)],check=True,**kw)
for unit in ['tabor-core-queue.service','tabor-native-scope-prerequisites.service','tabor-sbuild-proof.service','tabor-frozen-buildd-root.service','tabor-current-uapi-intake.service','tabor-sbuild-sequence.service','tabor-ready-batch.service']:
 r=subprocess.run(['python3',str(helper/'sudo.py'),shlex.join(['systemctl','is-active','--quiet',unit])],capture_output=True)
 assert r.returncode!=0,'Existing heavy task: '+unit
snapshot=base+'/submissions/'+a.run_id+'/project'
remote(['python3','-c','from pathlib import Path;Path('+repr(snapshot)+').mkdir(parents=True,exist_ok=False)'])
stream=io.BytesIO()
with tarfile.open(fileobj=stream,mode='w') as tar:
 for name in ['scripts/run-sbuild-package.py',
              'scripts/inspect-spe-package-payloads.py',str(spec.relative_to(project)),
              settings['source_lock'],settings['base_lock']]+([settings['configure_cache']['path']]+[e['path'] for e in settings['configure_cache']['evidence']] if settings.get('configure_cache') else [])+([settings['source_patch']['path']] if settings.get('source_patch') else []):
  tar.add(project/name,arcname=name)
 if settings.get('quilt_patch_series'):
  path=settings['quilt_patch_series']['path'];tar.add(project/path,arcname=path)
  for patch in json.loads((project/path).read_text())['patches']:tar.add(project/patch['path'],arcname=patch['path'])
remote(['tar','-xf','-','-C',snapshot],input=stream.getvalue())
remote(['systemd-run','--unit=tabor-sbuild-proof','--collect','--property=CPUQuota=400%',
        '--property=MemoryMax=6G','--property=TasksMax=256','--description=Debian sbuild package proof',
        'python3',snapshot+'/scripts/run-sbuild-package.py','--project',snapshot,'--base',base,
        '--spec',snapshot+'/'+str(spec.relative_to(project)),'--output',base+'/work/'+a.run_id],root=True)
print('Submitted standard sbuild proof:',a.run_id)
