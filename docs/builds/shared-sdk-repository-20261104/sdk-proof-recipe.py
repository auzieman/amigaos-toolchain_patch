from pathlib import Path
import json,subprocess,os,sys,hashlib
sys.path.insert(0,'/tmp/tabor-repository-proof-scripts')
from apt_archive_cache import mapped_root_ids
from sbuild_local_repository import digest
b=Path('/srv/data1/tabor-build/linux-live-001');o=b/'work/shared-sdk-namespace-proof-001';o.mkdir();rp=b/'work/shared-sdk-buildd-004/receipt.json';r=json.loads(rp.read_text());tar=rp.parent/'trixie-amd64.tar';assert digest(tar)==r['sha256'];parent=b.parent.parent/'tabor-sbuild-roots';root=parent/o.name;root.mkdir();uid,gid=mapped_root_ids('owner');os.chown(root,uid,gid);prefix=['runuser','-u','owner','--','/usr/libexec/sbuild-usernsexec'];maps=['u:0:'+str(uid)+':65536','g:0:'+str(gid)+':65536']
with tar.open('rb') as f:subprocess.run(prefix+maps+['--','tar','--exclude=./dev/*','-xf','-','-C',str(root)],stdin=f,check=True)
cmd=prefix+['--pivotroot','--nonet']+maps+[str(root),'root','/',r['shared_sdk']['path'],'/usr/lib/tabor-spe-toolchain','--','sh','-ec', '''test "$(dpkg-query -W -f='${Status} ${Version}' tabor-spe-toolchain)" = 'install ok installed 8.5.0+tabor6'
test -z "$(dpkg -V tabor-spe-toolchain)"
if touch /usr/lib/tabor-spe-toolchain/shared-write-test 2>/tmp/write-error; then exit 1; fi
grep 'Read-only file system' /tmp/write-error
printf '%s\n' '#include <stddef.h>' 'float spe_add(float a,float b) { return a+b; }' > /tmp/probe.c
powerpc-linux-gnuspe-gcc -mcpu=8540 -mabi=spe -mspe -mfloat-gprs=double -S /tmp/probe.c -o /tmp/probe.s
grep 'efsadd' /tmp/probe.s
dpkg --audit
''']
p=subprocess.run(cmd,capture_output=True,text=True);(o/'namespace.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stdout+p.stderr
(o/'receipt.json').write_text(json.dumps({'status':'shared-read-only-sdk-namespace-qualified','root_receipt_sha256':digest(rp),'command':cmd,'exit':p.returncode,'evidence':p.stdout,'scope':'actual sbuild UID maps and bind backend; real dpkg installed state/file verification, read-only filesystem rejection, target SPE assembly; no target execution; full sbuild package pending'},indent=2)+'\n');print(p.stdout)
