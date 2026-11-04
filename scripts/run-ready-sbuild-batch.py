#!/usr/bin/env python3
"""Dispatch only dose-ready sources, then let sbuild/apt install their build deps.

The Debian solver supplies readiness and dependency explanations. This controller
only bounds concurrency, retains outcomes and rechecks after the artifact pool
changes; it does not implement dependency resolution or execute target programs.
"""
import argparse,collections,concurrent.futures,hashlib,json,re,subprocess
from pathlib import Path
from build_failure_evidence import archive_failures
p=argparse.ArgumentParser(description=__doc__)
for n in ['project','base','plan','output']:p.add_argument('--'+n,type=Path,required=True)
a=p.parse_args();plan=json.loads(a.plan.read_text());a.output.mkdir(exist_ok=False)
assert 1<=plan['concurrency']<=4
indep=plan.get('build_mode','cross')=='indep'
registry=json.loads((a.project/plan['registry']).read_text()).get('packages',{}) if plan.get('registry') else {}
scope=json.loads((a.project/'profiles/port-build-scope.json').read_text()) if (a.project/'profiles/port-build-scope.json').exists() else {}
assert not (set(plan['packages']) & set(scope.get('deferred_candidates',{}))), 'Queue contains a deferred scope candidate'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'status':'running','plan_sha256':sha(a.plan),'items':[],'audits':[],
   'target_execution':False,'target_installation':False,'boot_image_ready':False,'qemu_launched':False}
def save():
 (a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
 view=a.base/'viewport-live-001/current.json'
 if view.parent.exists():
  done=sum(x['status']=='debian-packages-built-not-target-installed' for x in r['items'])
  failed=sum(x['status']=='failed-see-retained-log' for x in r['items'])
  running=[x['package'] for x in r['items'] if x['status']=='running']
  view.write_text(json.dumps({'iteration':', '.join(running) or r['status'],
   'runtime':f'Debian dependency-ready queue: {done} built, {failed} failed, {len(r.get("blocked",[]))} dependency-blocked; max {plan["concurrency"]} jobs',
   'viewer':'Package-managed new-image assembly and requested QEMU boot follow build/install acceptance'},indent=2)+'\n')
def scoped(cmd,unit,cpus,memory,logpath):
 with logpath.open('w') as log:
  result=subprocess.run(['systemd-run','--quiet','--wait','--pipe','--collect','--unit='+unit,
   '--property=CPUQuota='+str(cpus*100)+'%','--property=MemoryMax='+memory,'--property=TasksMax=256',*map(str,cmd)],stdout=log,stderr=subprocess.STDOUT).returncode
  if result:
   subprocess.run(['journalctl','--unit='+unit,'--no-pager','-n','30'],stdout=log,stderr=subprocess.STDOUT)
  return result
save()
try:
 defaults=json.loads((a.project/plan['defaults']).read_text())
 profile=json.loads((a.project/'profiles/images/debian-package-builder.json').read_text())
 audit=a.base/plan['initial_audit'];pr=json.loads((audit/'receipt.json').read_text())
 assert pr['status']=='debian-dependency-audit-completed'
 assert sha(audit/'NativePackages')==pr['native_packages_sha256']
 assert pr.get('build_mode','cross')==('indep' if indep else 'cross')
 assert sha(audit/'receipt.json')==plan['initial_audit_sha256']
 attempted=set()
 for wave in range(1,len(plan['packages'])+1):
  report=json.loads((audit/'dependency-report.json').read_text())
  assert sha(audit/'dependency-report.yaml')==pr['report_sha256']
  ready={x['package'] for x in report['report'] if x['status']=='ok'}
  architecture={x['package']:x['architecture'] for x in report['report']}
  candidates=[n for n in plan['packages'] if n not in attempted and n in ready and (indep or architecture.get(n)!='all')]
  r['blocked']=[x for x in report['report'] if x['package'] in plan['packages'] and x['package'] not in attempted and x['status']=='broken']
  r['data_only_pending']=[] if indep else [n for n in plan['packages'] if n not in attempted and architecture.get(n)=='all']
  if not candidates:break
  assert sha(audit/'build-pool-inputs.json')==pr['pool_inputs_sha256']
  pool=json.loads((audit/'build-pool-inputs.json').read_text());jobs=[]
  for name in candidates[:plan['concurrency']]:
   attempted.add(name);spec=json.loads(json.dumps(defaults));spec['package']=name
   settings=profile.get('package_inputs',{}).get(name,{})
   for key in ['source_lock','source_cache']:
    spec[key]=settings.get(key,profile[key])
   override=registry.get(name,{})
   if override.get('spec'):
    reviewed=json.loads((a.project/override['spec']).read_text())
    assert reviewed['package']==name
    for key in ['source_lock','source_cache','source_patch','quilt_patch_series']:
     if key in reviewed:spec[key]=reviewed[key]
   # Use the solver's actual installation set, not an invented name heuristic.
   solution=next(x for x in report['report'] if x['package']==name)
   spec['build_profiles']=solution.get('build_profiles','nocheck' if indep else 'cross,nocheck')
   spec['bootstrap']='stage1' in spec['build_profiles'].split(',')
   spec['required_full_rebuild']=spec['bootstrap']
   needed={(x['package'],x['version'],x['architecture']) for x in solution['installationset'] if x.get('type')!='src'}
   assert sha(audit/'build-pool-artifacts.json')==pr['pool_artifacts_sha256']
   artifacts=json.loads((audit/'build-pool-artifacts.json').read_text());files={}
   for artifact in artifacts:
    key=(artifact['package'],artifact['version'],artifact['architecture'])
    if key in needed:
     files.setdefault(artifact['receipt'],[]).append(artifact)
   selected=[]
   for entry in pool:
    choices=files.get(entry['receipt'],[])
    if choices:selected.append({**entry,'packages':sorted({x['package'] for x in choices}),'files':[x['file'] for x in choices]})
   spec['extra_receipts']=selected
   if indep:
    spec.update(indep_only=True,host_architecture='amd64',native_toolchain_inputs=[])
   if name in plan.get('patch_series',{}):spec['quilt_patch_series']=plan['patch_series'][name]
   if name not in plan['configure_cache_sources']:spec.pop('configure_cache',None)
   spec['binary_nmu']=0 if indep else override.get('binary_nmu',0)
   spec['scope']='Debian dose-ready cross build; apt installs real native/SPE development dependencies before compilation'
   fingerprint=hashlib.sha256((json.dumps(spec,sort_keys=True)+sha(a.project/'scripts/run-sbuild-package.py')).encode()).hexdigest()
   if any(x.get('package')==name and x.get('input_fingerprint')==fingerprint for x in plan.get('prior_failures',[])):
    r['items'].append({'package':name,'status':'deferred-unchanged-failure','input_fingerprint':fingerprint,'wave':wave,'exit':0})
    save();continue
   specpath=a.output/(name+'-spec.json');specpath.write_text(json.dumps(spec,indent=2)+'\n')
   work=a.base/'work'/(plan['run_prefix']+'-'+name)
   item={'package':name,'work':str(work),'status':'running','wave':wave,'input_fingerprint':fingerprint};r['items'].append(item);save()
   cmd=['python3',a.project/'scripts/run-sbuild-package.py','--project',a.project,'--base',a.base,'--spec',specpath,'--output',work]
   jobs.append((item,cmd,a.output/(name+'.log')))
  if not jobs:continue
  with concurrent.futures.ThreadPoolExecutor(max_workers=plan['concurrency']) as workers:
   futures={workers.submit(scoped,cmd,plan['unit_prefix']+'-'+item['package'],4,'6G',log):item for item,cmd,log in jobs}
   for future in concurrent.futures.as_completed(futures):
    item=futures[future];item['exit']=future.result()
    if item['exit']==0:
     receipt=Path(item['work'])/'receipt.json';record=json.loads(receipt.read_text())
     assert record['status']=='debian-packages-built-not-target-installed' and record.get('payload_inspection_sha256')
     item.update(status=record['status'],receipt_sha256=sha(receipt))
    else:
     item['status']='failed-see-retained-log'
     source_log=Path(item['work'])/'sbuild.log'
     with (source_log if source_log.exists() else a.output/(item['package']+'.log')).open(errors='replace') as f:
      tail=list(collections.deque(f,maxlen=700))
     errors=[s.strip()[:400] for s in tail if re.search(r'error:|FAILED:|undefined reference|cannot find|unsat-dependency:|Fail-Stage:|OOM|oom-kill|Permission denied|^E:|Depends:|trying to overwrite|dpkg: error|Not using sbuild-cross-resolver',s)]
     item['diagnostics']=errors[-8:]
     item['failure_stage']=next((s.split(':',1)[1].strip() for s in tail if s.startswith('Fail-Stage:')),'needs-review')
     journal=(a.output/(item['package']+'.log')).read_text(errors='replace')[-12000:]
     acquisition=archive_failures(source_log)
     item['archive_diagnostics']=acquisition
     text='\n'.join(errors+acquisition)+journal
     if re.search(r'oom-kill|OOM killer|Error creating chroot|Permission denied',text):category='infrastructure'
     elif re.search(r'Syntax error .*apt.conf|apt-utils.*not installed',text):category='build-root-configuration'
     elif acquisition:category='archive-acquisition'
     elif re.search(r'trying to overwrite|dpkg: error processing archive',text):category='package-coinstallation'
     elif item['failure_stage'] in ['install-deps','apt-get-update']:category='dependency-installation'
     elif re.search(r'dh_missing|dh_install:|dpkg-gencontrol:',text):category='packaging'
     elif re.search(r'error:|undefined reference',text):category='source-build'
     else:category='needs-review'
     item['failure_category']=category
    save()
  # Recompute with Debian's solver after newly built artifacts become available.
  pending=[name for name in plan['packages'] if name not in attempted]
  if not pending:
   r['blocked']=[]
   r['data_only_pending']=[]
   break
  next_audit=a.base/'work'/(plan['run_prefix']+'-dependencies-'+str(wave))
  cmd=['python3',a.project/'scripts/audit-sbuild-dependencies.py','--project',a.project,'--base',a.base,'--reuse-native-audit',audit,'--output',next_audit,'--sources',*pending]
  if indep:cmd.append('--indep-only')
  for key,flag in [('registry','--registry'),('prepared_sources','--prepared-sources')]:
   if plan.get(key):cmd.extend([flag,str(a.project/plan[key]) if key=='registry' else str(a.base/plan[key])])
  if plan.get('bootstrap'):cmd.append('--bootstrap')
  assert scoped(cmd,plan['unit_prefix']+'-audit',1,'3G',a.output/('audit-'+str(wave)+'.log'))==0
  audit=next_audit;pr=json.loads((audit/'receipt.json').read_text())
  r['audits'].append({'path':str(audit),'receipt_sha256':sha(audit/'receipt.json')});save()
 r['status']='completed-with-deferred-items' if r.get('blocked') or r.get('data_only_pending') or any(x.get('exit') or x['status']=='deferred-unchanged-failure' for x in r['items']) else 'completed'
except BaseException as error:r.update(status='interrupted-or-infrastructure-failed',error=str(error));raise
finally:save()
