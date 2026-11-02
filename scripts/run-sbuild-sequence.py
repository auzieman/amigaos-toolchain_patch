#!/usr/bin/env python3
"""Serial retained sbuild attempts; apt remains the dependency resolver.

Each source gets a fresh frozen root. Only accepted binary artifacts accumulate
as normal sbuild extra-package inputs. Failed sources are retained and the next
source still runs. This does not assemble or accept a target image.
"""
import argparse, hashlib, json, subprocess, time
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for n in ['project','base','plan','output']:p.add_argument('--'+n,type=Path,required=True)
a=p.parse_args();plan=json.loads(a.plan.read_text());a.output.mkdir(exist_ok=False)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
r={'status':'waiting-for-prerequisite','plan_sha256':sha(a.plan),'items':[],
   'target_installation':False,'boot_image_ready':False,'qemu_launched':False}
def save():
 (a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
 view=a.base/'viewport-live-001/current.json'
 if view.parent.exists():
  done=sum(x['status']=='debian-packages-built-not-target-installed' for x in r['items'])
  failed=sum(x['status']=='failed-see-retained-sbuild-log' for x in r['items'])
  view.write_text(json.dumps({'iteration':r['items'][-1]['package'] if r['items'] else 'waiting-for-libxcb',
    'runtime':f'Fixed-base X11 sequence: {done} built, {failed} deferred; '+r['status'],
    'viewer':'New image QEMU launch requested after package-managed assembly; this sequence builds dependencies'},indent=2)+'\n')
def accept(path):
 record=json.loads(path.read_text())
 assert record['status']=='debian-packages-built-not-target-installed'
 assert record.get('payload_inspection_sha256')==sha(path.parent/'payload-inspection.json')
 packages=[];allow_all=False
 for name in record['packages']:
  if not name.endswith('.deb'):continue
  f=path.parent/name
  assert sha(f)==record['packages'][name]['sha256']
  package,arch=subprocess.check_output(['dpkg-deb','-f',str(f),'Package','Architecture'],text=True).splitlines()
  # dpkg-deb labels fields when querying more than one.
  package=package.removeprefix('Package: ');arch=arch.removeprefix('Architecture: ')
  assert arch in ['powerpcspe','all'];allow_all |= arch=='all';packages.append(package)
 assert packages
 return {'receipt':str(path.relative_to(a.base)),'sha256':sha(path),'packages':packages,'allow_arch_all':allow_all}
save()
try:
 prerequisite=a.base/plan['prerequisite']
 deadline=time.monotonic()+7200
 while True:
  if prerequisite.exists():
   prior=json.loads(prerequisite.read_text())
   if prior['status']=='debian-packages-built-not-target-installed' and prior.get('payload_inspection_sha256'):break
   assert prior['status'] in ['preparing','sbuild-running','debian-packages-built-not-target-installed'],'Prerequisite failed'
  assert time.monotonic()<deadline,'Prerequisite timeout'
  time.sleep(10)
 extras=[accept(prerequisite)]
 defaults=json.loads((a.project/plan['defaults']).read_text())
 r['status']='running';save()
 for name in plan['packages']:
  spec=json.loads(json.dumps(defaults));spec['package']=name
  spec['scope']='Serial frozen-base sbuild sequence; apt resolves dependencies; no target/image acceptance'
  spec['extra_receipts']+=extras
  specpath=a.output/(name+'-spec.json');specpath.write_text(json.dumps(spec,indent=2)+'\n')
  work=a.base/'work'/(plan['run_prefix']+'-'+name)
  item={'package':name,'work':str(work),'status':'running'};r['items'].append(item);save()
  with (a.output/(name+'.log')).open('w') as log:
   result=subprocess.run(['python3',str(a.project/'scripts/run-sbuild-package.py'),
      '--project',str(a.project),'--base',str(a.base),'--spec',str(specpath),'--output',str(work)],stdout=log,stderr=subprocess.STDOUT)
  item['exit']=result.returncode
  if result.returncode==0:
   extras.append(accept(work/'receipt.json'));item['status']='debian-packages-built-not-target-installed'
  else:item['status']='failed-see-retained-sbuild-log'
  save()
 r['status']='completed' if all(i['exit']==0 for i in r['items']) else 'completed-with-deferred-items'
except BaseException as error:
 r.update(status='interrupted-or-prerequisite-failed',error=str(error));raise
finally:save()
