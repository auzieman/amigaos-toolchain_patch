import subprocess,runpy,json
from pathlib import Path
b=runpy.run_path('tabor-spe-toolchain/work/modular-usb-update-20261105-001/board_access.py')['base'];d=Path('tabor-spe-toolchain/docs/builds/mesa-systemic-boundaries-20261109')
def ssh(c,**kw):return subprocess.run(['ssh',*b,'root@192.168.1.249',c],**kw)
src='/srv/data1/tabor-build/linux-live-001/work/radeonsi-systemic-20261109-001/output/usr/lib/libgallium-25.0.7.so';dst='/opt/tabor-mesa-le-ib-20261109/usr/lib/libgallium-25.0.7.so'
h=subprocess.check_output(['python3','lab/consolidation-20261002/r730-prep-20261031/remote.py','sha256sum '+src],text=True).split()[0]
a=subprocess.Popen(['python3','lab/consolidation-20261002/r730-prep-20261031/remote.py','cat '+src],stdout=subprocess.PIPE)
r=ssh('set -e; mount -o remount,rw /; cp -p '+dst+' '+dst+'.before-float-mode; cat > '+dst+'.new; chmod 755 '+dst+'.new; mv '+dst+'.new '+dst+'; sync; mount -o remount,ro /; /sbin/busybox-modules sha256sum '+dst,stdin=a.stdout,capture_output=True,text=True,timeout=60);a.stdout.close();assert a.wait()==0;r.check_returncode();assert r.stdout.split()[0]==h;(d/'float-mode-runtime-readback.txt').write_text(r.stdout);print(r.stdout)
