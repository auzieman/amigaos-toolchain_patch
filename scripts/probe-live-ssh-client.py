#!/usr/bin/env python3
"""Use a native SSH client against a forwarded loopback guest; never copies the private key."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--port',type=int,required=True)
p.add_argument('--identity',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--cxx',action='store_true')
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
options=['-F','/dev/null','-i',str(a.identity),'-p',str(a.port),'-o','BatchMode=yes',
 '-o','IdentitiesOnly=yes','-o','PreferredAuthentications=publickey',
 '-o','StrictHostKeyChecking=accept-new','-o','UserKnownHostsFile='+str(a.output/'known_hosts'),
 '-o','ConnectTimeout=20']
r={'status':'started','physical_boot':False,'full_spe_abi_validated':False,
   'native_ssh_version':subprocess.run(['ssh','-V'],capture_output=True,text=True).stderr.strip()}
sha=lambda data:hashlib.sha256(data).hexdigest()
def test(name,command,pty=False):
    result=subprocess.run(['ssh',*options,'-n',*(['-tt'] if pty else []),'tabor@127.0.0.1',command],capture_output=True,timeout=90)
    (a.output/(name+'.stdout')).write_bytes(result.stdout)
    (a.output/(name+'.stderr')).write_bytes(result.stderr)
    r[name]={'returncode':result.returncode,'stdout_sha256':sha(result.stdout),'stderr_sha256':sha(result.stderr)}
    return result
try:
    result=test('identity',"grep '^Uid:' /proc/self/status; pwd; test -w . && echo SSH_HOME_OK")
    assert result.returncode==0 and re.search(rb'^Uid:\s+1000\s+1000\s+1000\s+1000$',result.stdout,re.M)
    assert b'/home/tabor\n' in result.stdout and b'SSH_HOME_OK\n' in result.stdout
    result=test('pty',"test -t 0 && printf 'SSH_PTY_OK\\n'",True)
    assert result.returncode==0 and b'SSH_PTY_OK' in result.stdout
    result=test('fractal','/bin/fractal-test')
    assert result.returncode==0 and b'FRACTAL_FAIL' not in result.stdout
    assert b'FRACTAL_CLI_DONE' in result.stdout
    trials=re.findall(rb'FRACTAL_TIME mode=(SOFT|SPE) trial=(\d+) us=(\d+) checksum=(\d+)',result.stdout)
    assert len(trials)==6 and all(int(v[3])==0xabd5de74 and int(v[2])>0 for v in trials)
    assert sorted((v[0],int(v[1])) for v in trials)==[(m,t) for m in [b'SOFT',b'SPE'] for t in [1,2,3]]
    images={m:bytes.fromhex(v.decode()) for m,v in re.findall(rb'FRACTAL_PIXELS mode=(SOFT|SPE) ([0-9a-f]+)',result.stdout)}
    assert len(images[b'SOFT'])==12288 and images[b'SOFT']==images[b'SPE']
    checksum=2166136261
    for n in images[b'SOFT']:checksum=((checksum^n)*16777619)&0xffffffff
    assert checksum==0xabd5de74
    r['fractal_pixel_equality']=True
    result=test('abi','/bin/spe-abi-check --cli')
    checks={name.decode():status.decode() for name,status in re.findall(rb'^ABI_TEST (\w+) ([A-Z_]+)$',result.stdout,re.M)}
    r['abi_check_status']=checks
    assert set(checks)=={'float32','float64','varargs','formatting','fenv','setjmp','signal','pthread_tls','ucontext'}
    assert all(v=='PASS' for k,v in checks.items() if k!='fenv')
    assert checks['fenv'] in ['PASS','FAIL'] and result.returncode==(0 if checks['fenv']=='PASS' else 1)
    r['full_spe_abi_validated']=False # broader ABI/unwinding and hardware gates remain separate
    r['basic_c_checks_all_passed']=all(v=='PASS' for v in checks.values())
    if a.cxx:
        result=test('cxx','/bin/spe-cxx-check --cli')
        checks={name.decode():value.decode() for name,value in re.findall(rb'^CXX_TEST (\w+) (PASS|FAIL)$',result.stdout,re.M)}
        r['cxx_check_status']=checks
        assert set(checks)=={'long_double_128','exception_unwind','thread_tls','atomic_u32'}
        assert result.returncode==0 and all(v=='PASS' for v in checks.values())
        assert b'CXX_SMOKE_DONE failures=0' in result.stdout
    r['status']='passed'
except Exception as error:
    r.update(status='failed',error=str(error));raise
finally:
    (a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
