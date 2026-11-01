#!/usr/bin/env python3
"""Test packaged shared libc privately in an existing guest; never install over its baseline."""
import argparse, hashlib, json, re, shlex, struct, subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for name in ['remote-helper','identity','known-hosts','output']:
 p.add_argument('--'+name,type=Path,required=True)
for name in ['build','guest-dir','dynamic-probe']:
 p.add_argument('--'+name,required=True)
p.add_argument('--port',type=int,required=True)
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
ssh=['ssh','-F','/dev/null','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(a.known_hosts),'-i',str(a.identity),'-p',str(a.port),'tabor@127.0.0.1']
def fetch(path):return subprocess.check_output(['python3',str(a.remote_helper),'cat '+shlex.quote(path)])
def execute(command):
 s=shlex.join(command)
 t=subprocess.run(ssh+['ulimit -c 0; '+s+'; result=$?; echo TABOR_EXIT=$result; exit 0'],capture_output=True,text=True,timeout=90,check=True)
 m=re.search(r'^TABOR_EXIT=(\d+)$',t.stdout,re.M);assert m
 return {'command':s,'exit':int(m[1]),'stdout':t.stdout,'stderr':t.stderr}
proof=json.loads(fetch(a.build+'/runtime-package-proof.json'));assert proof['status']=='package-runtime-match'
r={'status':'started','package_proof':proof,'scope':'Private runtime in existing system-QEMU; no package installation or hardware acceptance','tests':{}}
try:
 subprocess.run(ssh+['mkdir -p '+shlex.quote(a.guest_dir)],check=True)
 for name,digest in proof['files_sha256'].items():
  data=fetch(a.build+'/source/debian/libc6/usr/lib/powerpc-linux-gnuspe/'+name)
  assert hashlib.sha256(data).hexdigest()==digest
  dest=a.guest_dir+'/'+name
  subprocess.run(ssh+['cat > '+shlex.quote(dest)+'; chmod 755 '+shlex.quote(dest)],input=data,check=True)
  assert hashlib.sha256(subprocess.check_output(ssh+['cat '+shlex.quote(dest)])).hexdigest()==digest
 # A static executable cannot validate replacement shared libc.
 probe=subprocess.check_output(ssh+['cat '+shlex.quote(a.dynamic_probe)])
 assert probe[:6]==b'\x7fELF\x01\x02'
 off=struct.unpack_from('>I',probe,28)[0];size,count=struct.unpack_from('>HH',probe,42)
 assert any(struct.unpack_from('>I',probe,off+i*size)[0]==3 for i in range(count)), 'ABI probe must have PT_INTERP'
 r['dynamic_probe_sha256']=hashlib.sha256(probe).hexdigest()
 loader=[a.guest_dir+'/ld.so.1','--library-path',a.guest_dir+':/lib:/usr/lib']
 for name,command in [('baseline-cxx',['/bin/spe-cxx-check','--cli']),
  ('candidate-cxx-map',loader+['--list','/bin/spe-cxx-check']),
  ('candidate-abi-map',loader+['--list',a.dynamic_probe]),
  ('candidate-cxx',loader+['/bin/spe-cxx-check','--cli']),
  ('candidate-abi',loader+[a.dynamic_probe,'--cli'])]:
  r['tests'][name]=execute(command)
  (a.output/(name+'.log')).write_text(r['tests'][name]['stdout']+r['tests'][name]['stderr'])
 for name in ['baseline-cxx','candidate-cxx']:
  t=r['tests'][name];checks=dict(re.findall(r'^CXX_TEST (\w+) (PASS|FAIL)$',t['stdout'],re.M));assert t['exit']==0 and checks=={n:'PASS' for n in ['long_double_128','exception_unwind','thread_tls','atomic_u32']}, name
 for name in ['candidate-cxx-map','candidate-abi-map']:
  t=r['tests'][name];assert t['exit']==0 and a.guest_dir+'/libc.so.6' in t['stdout'] and a.guest_dir+'/libm.so.6' in t['stdout']
 t=r['tests']['candidate-abi'];checks=dict(re.findall(r'^ABI_TEST (\w+) (PASS|FAIL)$',t['stdout'],re.M));r['abi_checks']=checks
 assert all(checks.get(n)=='PASS' for n in ['float32','float64','varargs','formatting','setjmp','signal','pthread_tls','ucontext'])
 assert set(checks)=={'float32','float64','varargs','formatting','fenv','setjmp','signal','pthread_tls','ucontext'}
 assert t['exit']==(0 if checks['fenv']=='PASS' else 1)
 r['status']='unwind-fixed-fenv-open' if checks['fenv']=='FAIL' else 'basic-runtime-smoke-passed'
 r['full_spe_abi_validated']=False
except Exception as exc:r.update(status='failed',error=str(exc));raise
finally:(a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
print(r['status'])
for name,t in r['tests'].items():print(name,'exit='+str(t['exit']))
