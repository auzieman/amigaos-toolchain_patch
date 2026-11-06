#!/usr/bin/env python3
"""One controlled module test on an already booted diagnostic A1222.

Leaves the installed module tree untouched. Requires an explicit candidate,
expected hash, scoped host keys and private-key path. No forced module removal.
"""
import argparse,hashlib,json,subprocess,shlex
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,required=True);p.add_argument('--sha256',required=True)
p.add_argument('--key',required=True);p.add_argument('--known-hosts',required=True)
p.add_argument('--host',default='192.168.1.249');p.add_argument('--jump',default='root@192.168.1.15')
p.add_argument('--output',type=Path,required=True);a=p.parse_args()
assert hashlib.sha256(a.candidate.read_bytes()).hexdigest()==a.sha256
assert a.output.name.replace('-','').isalnum()
a.output.mkdir(parents=True,exist_ok=False)
opts=['-F','/dev/null','-J',a.jump,'-i',a.key,'-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+a.known_hosts]
host='root@'+a.host;remote='/root/'+a.output.name
q=shlex.quote
receipt={'candidate_sha256':a.sha256,'status':'started','installed_module_tree_changed':False}
def ssh(cmd,**kw):return subprocess.run(['ssh',*opts,host,cmd],check=True,**kw)
def fetch(name):subprocess.run(['scp','-q',*opts,host+':'+remote+'/'+name,str(a.output/name)],check=True)
pid=None
try:
 version=ssh('uname -r',capture_output=True,text=True).stdout.strip()
 assert version=='6.12.113-tabor-modular',version
 ssh('test ! -e '+q(remote)+' && mkdir '+q(remote))
 subprocess.run(['scp','-q',*opts,str(a.candidate),host+':'+remote+'/amdgpu-candidate.ko'],check=True)
 result=ssh('/sbin/busybox-modules sha256sum '+q(remote+'/amdgpu-candidate.ko'),capture_output=True,text=True).stdout
 assert result.split()[0]==a.sha256
 # Preserve continuous messages before touching the currently loaded module.
 pid=ssh('cat /dev/kmsg > '+q(remote+'/kmsg.txt')+' 2> '+q(remote+'/kmsg.stderr')+' < /dev/null & echo $!',capture_output=True,text=True).stdout.strip()
 assert pid.isdigit()
 with (a.output/'load-result.txt').open('w') as f:
  ssh('rmmod amdgpu && insmod '+q(remote+'/amdgpu-candidate.ko')+'; echo TEST_RC=$?; cat /proc/modules; cat /proc/fb; ls -l /sys/bus/pci/devices/0001:01:00.0/driver; uname -r; cat /proc/uptime',stdout=f,stderr=subprocess.STDOUT,timeout=45)
 receipt['status']='test-executed-review-device-state'
finally:
 if pid:
  try:ssh('kill '+pid+'; sync');fetch('kmsg.txt');fetch('kmsg.stderr')
  except Exception as e:receipt['capture_cleanup_error']=str(e)
 (a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
