from pathlib import Path
import subprocess,hashlib,json
w=Path('/srv/data1/tabor-build/linux-live-001/work/mesa-3d-contracts-20261109-001')
b=Path('/srv/data1/tabor-build/linux-live-001')
gcc=str(b/'tools/cxx-reference-002/bin/powerpc-linux-gnuspe-gcc')
flags=['--sysroot='+str(b/'sysroot'),'-O2','-fPIC','-mcpu=8548','-mabi=spe','-mspe','-mfloat-gprs=double','-mlong-double-128']
for name in ['offline-stat32','offline-stat64']:
 subprocess.run([gcc,*flags,'-c',str(w/(name+'.c')),'-o',str(w/(name+'.o'))],check=True)
subprocess.run([gcc,*flags,'-shared',str(w/'offline-stat32.o'),str(w/'offline-stat64.o'),'-ldl','-o',str(w/'offline-stat-compat.so')],check=True)
(w/'offline-stat-build.json').write_text(json.dumps({'sha256':hashlib.sha256((w/'offline-stat-compat.so').read_bytes()).hexdigest(),'scope':'offline no-op DRM time64 stat/ioctl adapter only; no board deployment'},indent=2)+'\n')
