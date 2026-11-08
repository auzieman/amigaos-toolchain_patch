"""Read pinned R730 source; centralize ATOM encoding and audit kernel I/O edge."""
from pathlib import Path
import difflib,hashlib,json,re,subprocess
S=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-001/source')
O=Path('/srv/data1/tabor-build/source-review/shared-kernel-boundary-20261108');O.mkdir(parents=True,exist_ok=True)
pp='drivers/gpu/drm/amd/pm/powerplay/hwmgr/ppatomctrl.c';ah='drivers/gpu/drm/amd/amdgpu/atom.h';ac='drivers/gpu/drm/amd/amdgpu/amdgpu_atombios.c'
p=(S/pp).read_text();header=(S/ah).read_text();a=(S/ac).read_text();changes={}
start=p.index('/* The ATOM parameter word is LE:');end=p.index('union voltage_object_info',start)
helper=p[start:end].replace('static void atomctrl_set_clock_word','static inline void amdgpu_atom_set_clock_word').replace('static uint32_t atomctrl_clock_word_frequency','static inline uint32_t amdgpu_atom_clock_word_frequency').replace('static uint8_t atomctrl_clock_word_flags','static inline uint8_t amdgpu_atom_clock_word_flags')
hfixed=header.replace('#include <linux/types.h>','#include <linux/types.h>\n#include <linux/unaligned.h>\n\n'+helper.rstrip(),1)
pfixed=p[:start]+p[end:]
for old,new in [('atomctrl_set_clock_word','amdgpu_atom_set_clock_word'),('atomctrl_clock_word_frequency','amdgpu_atom_clock_word_frequency'),('atomctrl_clock_word_flags','amdgpu_atom_clock_word_flags')]:pfixed=pfixed.replace(old,new)
pfixed=pfixed.replace('#include <linux/unaligned.h>\n','')
# Fix the same word contract in the ASIC clock path used by vi_set_uvd_clock
# and vi_set_vce_clocks, rather than altering the video-engine packet format.
afixed=a
pairs=[('args.v4.ulClock = cpu_to_le32(clock);\t/* 10 khz */','amdgpu_atom_set_clock_word(&args.v4, clock, 0);'),('dividers->post_divider = dividers->post_div = args.v4.ucPostDiv;','dividers->post_divider = dividers->post_div =\n\t\t\tamdgpu_atom_clock_word_flags(&args.v4);'),('le32_to_cpu(args.v4.ulClock)','amdgpu_atom_clock_word_frequency(&args.v4)'),('args.v6_in.ulClock.ulComputeClockFlag = clock_type;\n\t\targs.v6_in.ulClock.ulClockFreq = cpu_to_le32(clock);\t/* 10 khz */','amdgpu_atom_set_clock_word(&args.v6_in.ulClock, clock, clock_type);'),('le32_to_cpu(args.v6_out.ulClock.ulClock)','amdgpu_atom_clock_word_frequency(&args.v6_out.ulClock)'),('args.v6_out.ulClock.ucPostDiv','amdgpu_atom_clock_word_flags(&args.v6_out.ulClock)')]
for old,new in pairs:
 assert old in afixed,old
 afixed=afixed.replace(old,new)
# Preserve the old whole-word case2/3/5 path, an independent known-style control.
assert afixed.count('args.v3.ulClockParams = cpu_to_le32((clock_type << 24) | clock);')==a.count('args.v3.ulClockParams = cpu_to_le32((clock_type << 24) | clock);')
changes={ah:(header,hfixed),pp:(p,pfixed),ac:(a,afixed)}
patch=''.join(''.join(difflib.unified_diff(x.splitlines(True),y.splitlines(True),fromfile='a/'+n,tofile='b/'+n)) for n,(x,y) in changes.items())
patchpath=O/'0022-amdgpu-share-atom-clock-word-boundary.patch';patchpath.write_text(patch)
subprocess.run(['git','apply','--check',str(patchpath)],cwd=S,check=True)
for n,(x,y) in changes.items():(O/(Path(n).name+'.fixed')).write_text(y)
# Save actual compiled I/O access functions, not an inference from architecture names.
obj=S.parent/'output/drivers/gpu/drm/amd/amdgpu/amdgpu_device.o'
names=[x.split()[-1] for x in subprocess.check_output(['powerpc-linux-gnu-nm',str(obj)],text=True).splitlines() if len(x.split())>=3]
def disassemble(prefix):
 return '\n'.join(subprocess.check_output(['powerpc-linux-gnu-objdump','-dr','--disassemble='+n,str(obj)],text=True) for n in names if n==prefix or n.startswith(prefix+'.'))
asm=disassemble('amdgpu_device_wreg')
assert 'stwbrx' in asm
(O/'mmio-write-disassembly.txt').write_text(asm)
asmr=disassemble('amdgpu_device_rreg')
assert 'lwbrx' in asmr
(O/'mmio-read-disassembly.txt').write_text(asmr)
receipt={'source':str(S),'patch_sha256':hashlib.sha256(patch.encode()).hexdigest(),'inputs':{n:hashlib.sha256(x.encode()).hexdigest() for n,(x,y) in changes.items()},'outputs':{n:hashlib.sha256(y.encode()).hexdigest() for n,(x,y) in changes.items()},'real_object_sha256':hashlib.sha256(obj.read_bytes()).hexdigest(),'compiled_mmio_write_byte_reverse_present':True,'compiled_mmio_read_byte_reverse_present':True,'global_mmio_dma_helpers_changed':False,'hardware_tested':False}
(O/'prepare.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
