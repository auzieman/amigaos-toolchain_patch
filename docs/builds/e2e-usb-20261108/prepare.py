from pathlib import Path
import subprocess,json,hashlib
parent=Path('/srv/data1/tabor-build/linux-live-001/work/atom-channel-20261108-002')
w=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-001')
assert not w.exists()
assert json.loads((parent/'build.json').read_text())['status']=='compiled-crcs-verified-not-deployed'
w.mkdir()
for name in ['source','output']:
 subprocess.run(['cp','-a','--reflink=auto',str(parent/name),str(w/name)],check=True)
print(str(w))
