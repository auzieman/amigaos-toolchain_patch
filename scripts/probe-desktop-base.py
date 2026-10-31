#!/usr/bin/env python3
"""Run the source-built desktop prerequisite probe in an existing SSH guest."""
import argparse,hashlib,json,shlex,subprocess,uuid
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for n in ['payload','key','known-hosts','output']:p.add_argument('--'+n,type=Path,required=True)
p.add_argument('--port',type=int,required=True);p.add_argument('--host-key-alias',default='[127.0.0.1]:12224');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
ssh=['ssh','-F','/dev/null','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','ConnectTimeout=10','-o','StrictHostKeyChecking=yes','-o','HostKeyAlias='+a.host_key_alias,'-o','UserKnownHostsFile='+str(a.known_hosts),'-i',str(a.key),'-p',str(a.port),'tabor@127.0.0.1']
dest='/tmp/desktop-base-'+uuid.uuid4().hex
files={'desktop-base-check':'desktop-base-check','stage/usr/lib/libz.so.1.3.1':'libz.so.1','stage/usr/lib/libpng16.so.16.48.0':'libpng16.so.16','stage/usr/lib/libpixman-1.so.0.44.0':'libpixman-1.so.0'}
r={'status':'started','physical_boot':False,'full_abi_validated':False,'guest_directory':dest,'inputs':{}}
try:
 subprocess.run(ssh+['mkdir '+shlex.quote(dest)],check=True,timeout=20)
 for local,remote in files.items():
  f=a.payload/local;data=f.read_bytes();assert data[:6]==b'\x7fELF\x01\x02' and data[18:20]==b'\x00\x14',f
  r['inputs'][remote]=hashlib.sha256(data).hexdigest()
  subprocess.run(ssh+['cat > '+shlex.quote(dest+'/'+remote)],input=data,check=True,timeout=45)
 command='chmod 700 '+shlex.quote(dest+'/desktop-base-check')+' && LD_LIBRARY_PATH='+shlex.quote(dest)+' '+shlex.quote(dest+'/desktop-base-check')
 result=subprocess.run(ssh+[command],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
 (a.output/'guest.log').write_bytes(result.stdout)
 text=result.stdout.decode(errors='replace');print(text,end='')
 checks=['zlib_roundtrip','png_rgba_roundtrip','pixman_argb_copy']
 assert result.returncode==0 and all('DESKTOP_BASE_TEST '+x+' PASS' in text for x in checks)
 r.update(status='passed-selected-software-prerequisite-checks',checks=checks,guest_log_sha256=hashlib.sha256(result.stdout).hexdigest())
except Exception as e:r.update(status='failed',error=str(e));raise
finally:(a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
