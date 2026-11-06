from pathlib import Path
import sys,subprocess,json,hashlib,shlex
w=Path(__file__).resolve().parent
sys.path.insert(0,str(w.parent/'modular-usb-update-20261105-001'));from board_access import ssh,scp
base='/srv/data1/tabor-build/linux-live-001/work/full-amd-firmware-20261105-001/'
helper='lab/consolidation-20261002/r730-prep-20261031/remote.py'
for n in ['manifest.json','receipt.json']:
 with (w/n).open('wb') as f:subprocess.run(['python3',helper,'cat '+base+n],stdout=f,check=True)
m=json.loads((w/'manifest.json').read_text());r=json.loads((w/'receipt.json').read_text())
# Existing hardware-file audit precedes installation.
paths=['/lib/firmware/'+n for n in m['module_polaris_requests']]
result=ssh(shlex.join(['/sbin/busybox-modules','sha256sum',*paths]),capture_output=True,text=True).stdout
(w/'polaris-before.txt').write_text(result)
expected={('/'+e['path']):e['sha256'] for e in m['firmware_files']}
observed={line.split(None,1)[1].strip():line.split()[0] for line in result.splitlines()}
assert all(observed[p]==expected[p] for p in paths)
print('All42 existing Polaris10/11 firmware requests already match the pinned package.',flush=True)
with (w/'firmware-payload.tar').open('wb') as f:subprocess.run(['python3',helper,'cat '+base+'firmware-payload.tar'],stdout=f,check=True)
assert hashlib.sha256((w/'firmware-payload.tar').read_bytes()).hexdigest()==r['payload_sha256']
remote='/root/full-amd-firmware-20261105-001'
ssh('test ! -e '+remote+' && mkdir '+remote)
scp(str(w/'firmware-payload.tar'),'root@192.168.1.249:'+remote+'/firmware-payload.tar')
check=ssh('/sbin/busybox-modules sha256sum '+remote+'/firmware-payload.tar',capture_output=True,text=True).stdout
assert check.split()[0]==r['payload_sha256']
# Copy rather than change the firmware search path; retain the original subset.
ssh('set -e; cp -a /lib/firmware '+remote+'/firmware-before; /sbin/busybox-modules tar -xf '+remote+'/firmware-payload.tar -C /; mkdir -p /usr/lib; if test ! -e /usr/lib/firmware; then ln -s /lib/firmware /usr/lib/firmware; fi; sync')
observed={}
entries=m['firmware_files']
with (w/'all-installed-hashes.txt').open('w') as f:
 for i in range(0,len(entries),40):
  names=['/'+e['path'] for e in entries[i:i+40]]
  out=ssh(shlex.join(['/sbin/busybox-modules','sha256sum',*names]),capture_output=True,text=True).stdout
  f.write(out)
  for line in out.splitlines():h,n=line.split(None,1);observed[n.strip()]=h
assert all(observed[p]==h for p,h in expected.items())
r.update(status='installed-all-firmware-readback-verified',verified_files=len(observed),original_polaris42_already_matched=True,graphics_tested=False)
(w/'installation-receipt.json').write_text(json.dumps(r,indent=2)+'\n')
scp(str(w/'installation-receipt.json'),'root@192.168.1.249:'+remote+'/installation-receipt.json')
scp(str(w/'manifest.json'),'root@192.168.1.249:'+remote+'/manifest.json')
ssh('sync; df -k /')
print('Complete firmware payload installed; all892 firmware files verified.',flush=True)
