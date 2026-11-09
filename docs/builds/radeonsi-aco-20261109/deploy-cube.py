import subprocess,runpy,hashlib
from pathlib import Path
b=runpy.run_path('tabor-spe-toolchain/work/modular-usb-update-20261105-001/board_access.py')['base'];src='/srv/data1/tabor-build/linux-live-001/work/kmscube-build-20261109-001/output/usr/bin/kmscube'
a=subprocess.Popen(['python3','lab/consolidation-20261002/r730-prep-20261031/remote.py','cat '+src],stdout=subprocess.PIPE)
r=subprocess.run(['ssh',*b,'root@192.168.1.249','set -e; mount -o remount,rw /; cat > /opt/tabor-radeonsi-20261109/usr/bin/kmscube; sync; mount -o remount,ro /; /sbin/busybox-modules sha256sum /opt/tabor-radeonsi-20261109/usr/bin/kmscube'],stdin=a.stdout,capture_output=True,text=True);a.stdout.close();assert a.wait()==0;r.check_returncode();h=subprocess.check_output(['python3','lab/consolidation-20261002/r730-prep-20261031/remote.py','sha256sum '+src],text=True).split()[0];assert h==r.stdout.split()[0];print(r.stdout)
