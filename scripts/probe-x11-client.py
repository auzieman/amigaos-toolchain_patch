#!/usr/bin/env python3
"""Execute the staged SPE client against a private native headless X server."""
import argparse,hashlib,json,shlex,subprocess,uuid
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for n in ['payload','key','known-hosts','output']:p.add_argument('--'+n,type=Path,required=True)
p.add_argument('--server-scope',default='separate native Xvfb, not target Xorg');p.add_argument('--host-key-alias',default='[127.0.0.1]:12224');p.add_argument('--port',type=int,required=True);p.add_argument('--display',default='10.0.2.2:117');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
ssh=['ssh','-F','/dev/null','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','ConnectTimeout=10','-o','StrictHostKeyChecking=yes','-o','HostKeyAlias='+a.host_key_alias,'-o','UserKnownHostsFile='+str(a.known_hosts),'-i',str(a.key),'-p',str(a.port),'tabor@127.0.0.1']
r={'status':'started','display':a.display,'server_scope':a.server_scope,'physical_boot':False,'full_abi_validated':False,'files':{}};dest='/tmp/x11-client-'+uuid.uuid4().hex
try:
 subprocess.run(ssh+['mkdir '+dest+' && mkdir '+dest+'/lib'],check=True,timeout=20)
 for f in sorted(a.payload.rglob('*')):
  if not f.is_file():continue
  name=str(f.relative_to(a.payload));assert name=='x11-client-check' or (f.parent==a.payload/'lib' and name.startswith('lib/'))
  data=f.read_bytes();assert data[:6]==b'\x7fELF\x01\x02' and data[18:20]==b'\x00\x14'
  r['files'][name]=hashlib.sha256(data).hexdigest()
  subprocess.run(ssh+['cat > '+shlex.quote(dest+'/'+name)],input=data,check=True,timeout=45)
 command='chmod 700 '+dest+'/x11-client-check && LD_LIBRARY_PATH='+dest+'/lib '+dest+'/x11-client-check '+shlex.quote(a.display)
 result=subprocess.run(ssh+[command],capture_output=True,timeout=45);text=result.stdout+result.stderr
 (a.output/'guest.log').write_bytes(text);print(text.decode(errors='replace'),end='')
 tests=['xlib_pixel_roundtrip','render_randr_fixes_protocol','xcb_request_reply']
 assert result.returncode==0 and all(('X11_CLIENT_TEST '+t+' PASS').encode() in text for t in tests)
 r.update(status='passed-SPE-client-protocol',tests=tests,guest_log_sha256=hashlib.sha256(text).hexdigest())
except Exception as e:r.update(status='failed',error=str(e));raise
finally:(a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
