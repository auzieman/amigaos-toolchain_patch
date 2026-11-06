import pathlib,subprocess,shutil,json,gzip,hashlib,struct,zlib
b=pathlib.Path('/base'); w=b/'work/tabor-modular-stage-20261105-001';w.mkdir()
k=b/'work/tabor-modular-20261105-003';o=k/'output';s=k/'source';image='sha256:2781e11839beffa351f8c411d71b7e2bd1ae0336d24c60b407778c3350dd9da0'
def run(c):subprocess.run(c,check=True)
# Distinct output tree and exact matching module dependency metadata.
run(['make','-C',str(s),'O='+str(o),'ARCH=powerpc','CROSS_COMPILE=powerpc-linux-gnu-','INSTALL_MOD_PATH='+str(w/'root'),'modules_install'])
run(['depmod','-b',str(w/'root'),'6.12.113-tabor-modular'])
run(['powerpc-linux-gnu-objcopy','-O','binary',str(o/'vmlinux'),str(w/'kernel.bin')])
elf=(o/'vmlinux').read_bytes();ph=struct.unpack_from('>I',elf,28)[0];ps,pn=struct.unpack_from('>HH',elf,42);loads=[struct.unpack_from('>8I',elf,ph+i*ps) for i in range(pn)];end=max(x[3]+x[5] for x in loads if x[0]==1);assert end<0x4000000
(w/'kernel.gz').write_bytes(gzip.compress((w/'kernel.bin').read_bytes(),mtime=0))
run(['mkimage','-A','ppc','-O','linux','-T','kernel','-C','gzip','-a','0','-e','0','-n','Tabor modular graphics','-d',str(w/'kernel.gz'),str(w/'uImage-modular')])
# Retain known boot arguments, staging addresses and firmware; change only kernel path.
cmd=pathlib.Path('/early/boot.cmd').read_text().replace('/boot/uImage','/boot/uImage-modular')
(w/'boot-modular.cmd').write_text(cmd)
run(['mkimage','-A','ppc','-T','script','-C','none','-n','Tabor modular USB','-d',str(w/'boot-modular.cmd'),str(w/'boot-modular.scr')])
# Module tools are a separate static binary, preserving the existing rescue shell.
run(['tar','-xjf',str(b/'cache/busybox-1.37.0.tar.bz2'),'-C',str(w)])
bs=w/'busybox-1.37.0';bo=w/'busybox-obj';bo.mkdir();cfg=(b/'work/rescue-005/obj/.config').read_text()
import re
for name in ['INSMOD','RMMOD','LSMOD','MODPROBE','DEPMOD','FEATURE_MODUTILS_ALIAS','FEATURE_MODUTILS_SYMBOLS','FEATURE_MODPROBE_BLACKLIST','SHA256SUM']:
 cfg=re.sub(r'^(?:# CONFIG_'+name+r' is not set|CONFIG_'+name+r'=.*)$','CONFIG_'+name+'=y',cfg,flags=re.M)
cfg=cfg.replace('CONFIG_DEFAULT_MODULES_DIR=""','CONFIG_DEFAULT_MODULES_DIR="/lib/modules"').replace('CONFIG_DEFAULT_DEPMOD_FILE=""','CONFIG_DEFAULT_DEPMOD_FILE="modules.dep"')
(bo/'.config').write_text(cfg)
make=['make','-C',str(bs),'O='+str(bo),'CROSS_COMPILE=/tools/reference-001/bin/powerpc-linux-gnuspe-','CONFIG_EXTRA_CFLAGS=--sysroot=/sysroot -isystem /sysroot/usr/include -B/sysroot/usr/lib/ -mcpu=8548 -mabi=spe -mspe -mfloat-gprs=double -mlong-double-128','CONFIG_EXTRA_LDFLAGS=--sysroot=/sysroot']
run(make+['oldconfig']);run(make+['-j4'])
shutil.copy2(bo/'busybox',w/'busybox-modules')
run(['tar','-cf',str(w/'modules.tar'),'-C',str(w/'root'),'lib/modules/6.12.113-tabor-modular'])
files=['uImage-modular','boot-modular.scr','boot-modular.cmd','busybox-modules','modules.tar']
r={'status':'staged','kernel_memory_end':hex(end),'files':{f:hashlib.sha256((w/f).read_bytes()).hexdigest() for f in files}}
(w/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
