import hashlib,json,os,re,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1];run=os.environ['BKC_RUN_ID']
assert re.fullmatch('[a-f0-9-]+',run)
m=json.loads((root/'source.json').read_text());h=m['sha256'];assert re.fullmatch('[a-f0-9]{64}',h)
ssh=['ssh','-i','/app/keys/bkc_id_rsa','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(root/'known_hosts'),'root@192.168.1.15']
bundle='/var/lib/bkc/tabor-inputs/'+h+'.tar';stage='/var/lib/bkc/tabor-build/'+run
assert subprocess.check_output(ssh+['sha256sum '+bundle],timeout=30).decode().split()[0]==h
subprocess.run(ssh+['install -d -m 0700 '+stage+' && tar -xf '+bundle+' -C '+stage+' && ln -s /var/lib/bkc/tabor-source-cache '+stage+'/cache'],check=True,timeout=90)
rc=subprocess.run(ssh+['sh '+stage+'/project/scripts/lab-iteration.sh '+stage],timeout=3300).returncode
out=root/'artifacts'/run;out.mkdir(parents=True,exist_ok=True)
data=subprocess.check_output(ssh+['tar -czf - -C '+stage+'/results .'],timeout=90)
(out/'iteration-results.tgz').write_bytes(data)
(out/'source.json').write_text(json.dumps(m,indent=2)+'\n')
print('REMOTE_STAGE',stage,'ARTIFACTS',out,'BUILD_EXIT',rc,flush=True)
if rc:raise SystemExit(rc)
