"""R730-only aggregate codec/replay preflight; incomplete coverage blocks deployment."""
from pathlib import Path
import subprocess,json,os,resource,time
W=Path('/srv/data1/tabor-build/source-review/trace-replay-20261108')
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3))
suites=[
 ('atom-clock','/home/owner/test-shared-atom-contracts.py','/srv/data1/tabor-build/source-review/shared-kernel-boundary-20261108/tests.json'),
 ('ring-contract','/home/owner/standalone-gpu-codec-20261108/run.py','/srv/data1/tabor-build/source-review/standalone-gpu-codec-20261108/receipt.json'),
 ('encoder-contract','/home/owner/test-uvd-encoder-codec.py','/srv/data1/tabor-build/source-review/uvd-encoder-codec-20261108/receipt.json'),
 ('clock-table-pipeline','/home/owner/test-clock-table-pipeline.py','/srv/data1/tabor-build/source-review/clock-table-pipeline-20261108/receipt.json'),
 ('native-state-decode','/home/owner/test-state-clock-decode.py','/srv/data1/tabor-build/source-review/state-clock-decode-20261108/receipt.json'),
 ('smu-transport','/home/owner/review-smu-flow.py','/srv/data1/tabor-build/source-review/smu-flow-review-20261108/receipt.json'),
 ('captured-replay','/home/owner/replay-smu-trace.py',str(W/'receipt.json'))]
report={'status':'BLOCKED','hardware_accessed':False,'deployment_allowed':False,'resource_bounds':{'cpus':1,'address_space_gib':6},'suites':[]}
for name,script,receipt in suites:
 started=time.monotonic()
 with (W/('preflight-'+name+'.log')).open('wb') as log:
  c=subprocess.run(['python3',script],stdout=log,stderr=subprocess.STDOUT,timeout=180)
 entry={'name':name,'exit':c.returncode,'elapsed_seconds':round(time.monotonic()-started,2)}
 if c.returncode==0:
  r=json.loads(Path(receipt).read_text());entry['status']=r['status'] if 'status' in r else r['sender_replay']
 else:entry['status']='FAIL'
 report['suites'].append(entry)
r=json.loads((W/'receipt.json').read_text())
report['missing_coverage']=r['missing_coverage']
report['codec_suites_passed']=all(s['status']=='PASS' for s in report['suites'])
report['reason']='Known encoding/replay checks pass, but complete table/ATOM/device-state coverage is not captured.' if report['codec_suites_passed'] else 'A codec/replay suite failed.'
(W/'preflight.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
raise SystemExit(2) # A passing subset must never authorize another deployment.
