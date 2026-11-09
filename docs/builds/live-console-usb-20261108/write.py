"""R730: wait for verified image, then write only the authorized second USB."""
from pathlib import Path
import json,os,subprocess,time
w=Path('/srv/data1/tabor-build/linux-live-001/work/live-console-usb-20261108-001')
for _ in range(120):
 if (w/'receipt.json').exists():break
 time.sleep(2)
else:raise RuntimeError('Image did not finish; USB not written')
d=json.loads((w/'receipt.json').read_text());assert d['status']=='console-image-built-not-booted',d.get('error')
assert d['default_release']=='6.12.113-tabor-e2e-008'
cmd=['/usr/bin/python3','/home/owner/live-console-usb-20261108/write-verified-usb.py','--image',d['image'],'--device','/dev/disk/by-id/usb-SanDisk_Cruzer_Glide_03007431041721021451-0:0','--receipt',str(w/'usb-write.json'),'--image-sha256',d['image_sha256'],'--expected-serial','SanDisk_Cruzer_Glide_03007431041721021451-0:0','--write']
props=dict(x.split('=',1) for x in subprocess.check_output(['udevadm','info','--query=property','--name',cmd[cmd.index('--device')+1]],text=True).splitlines() if '=' in x)
assert props.get('ID_SERIAL_SHORT')=='03007431041721021451'
# Full udev ID is recorded by udev; exact short serial remains the fixed guard.
cmd[cmd.index('--expected-serial')+1]=props['ID_SERIAL']
os.execv(cmd[0],cmd)
