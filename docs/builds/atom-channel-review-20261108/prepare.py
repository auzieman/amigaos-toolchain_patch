"""Run on R730: read pinned source, produce review patches and compiled contracts."""
from pathlib import Path
import difflib, hashlib, json, re, subprocess
BASE = Path('/srv/data1/tabor-build/linux-live-001/work/polaris-powerplay-20261108-003')
SRC = BASE/'source'
OUT = Path('/srv/data1/tabor-build/source-review/atom-channel-review-20261108')
OUT.mkdir(parents=True, exist_ok=True)
def sha(b): return hashlib.sha256(b).hexdigest()
def patch(name, path, before, after):
    assert before != after
    text=''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),fromfile='a/'+path,tofile='b/'+path))
    (OUT/name).write_text(text)
    r=subprocess.run(['git','apply','--check',str(OUT/name)],cwd=SRC,capture_output=True,text=True)
    assert r.returncode == 0, r.stderr
    return {'sha256':sha(text.encode()),'input_sha256':sha(before.encode()),'output_sha256':sha(after.encode())}
pp='drivers/gpu/drm/amd/pm/powerplay/'
rel=pp+'smumgr/polaris10_smumgr.c'; original=(SRC/rel).read_text()
header=(SRC/(pp+'inc/smu74_discrete.h')).read_text()
# Actual packed struct fields define widths; do not swap entire mixed-width rows.
def fields(name):
    body=re.search(r'struct '+name+r' \{(.*?)\n\};',header,re.S).group(1)
    return re.findall(r'(SMU_VoltageLevel|SMU_SclkSetting|uint(?:8|16|32)_t)\s+(\w+);',body)
def convert(value, typ):
    if typ=='uint8_t':return value.strip()
    width={'SMU_VoltageLevel':4,'uint32_t':4,'uint16_t':2}[typ]
    n=int(value.strip(),0);semantic=int.from_bytes(n.to_bytes(width,'little'),'big')
    return f'cpu_to_be{width*8}(0x{semantic:0{width*2}x})'
def convert_row(text, names):
    tokens=[x.strip() for x in text.split(',')]
    assert len(tokens)==len(names),(len(tokens),names)
    return ', '.join(convert(v,t) for v,(t,n) in zip(tokens,names))
gfx_fields=fields('SMU74_Discrete_GraphicsLevel');sclk_fields=fields('SMU_SclkSetting');mem_fields=fields('SMU74_Discrete_MemoryLevel')
assert gfx_fields[-1]==('SMU_SclkSetting','SclkSetting')
arr_re=r'(static const SMU74_Discrete_GraphicsLevel avfs_graphics_level_polaris10\[8\] = \{)(.*?)(\n\};)'
m=re.search(arr_re,original,re.S)
body=m.group(2)
rows=re.findall(r'\{\s*([^{}]+),\s*\{\s*([^{}]+)\s*\}\s*\}',body)
assert len(rows)==8
newbody=re.sub(r'\{\s*([^{}]+),\s*\{\s*([^{}]+)\s*\}\s*\}', lambda row: '{ '+convert_row(row.group(1),gfx_fields[:-1])+', { '+convert_row(row.group(2),sclk_fields)+' } }', body)
assert newbody!=body
fixed=original[:m.start(2)]+newbody+original[m.end(2):]
mem_re=r'(static const SMU74_Discrete_MemoryLevel avfs_memory_level_polaris10 = \{)\s*([^{}]+)(\};)'
mm=re.search(mem_re,fixed,re.S);fixed=fixed[:mm.start(2)]+convert_row(mm.group(2).strip(),mem_fields)+fixed[mm.end(2):]
fixed=fixed.replace('vr_config = 0x01000500; /* Real value:0x50001 */','vr_config = cpu_to_be32(0x00050001);')
fixed=fixed.replace('static const SMU74_Discrete_GraphicsLevel avfs_graphics_level_polaris10', '/* Calibration tables contain SMC big-endian bytes on every CPU. */\nstatic const SMU74_Discrete_GraphicsLevel avfs_graphics_level_polaris10',1)
receipt={'source':str(SRC),'patches':{}}
receipt['patches']['0019-polaris-avfs-calibration-byte-order.patch']=patch('0019-polaris-avfs-calibration-byte-order.patch',rel,original,fixed)
(OUT/'polaris10_smumgr.fixed.c').write_text(fixed)

# The ATOM interpreter consumes little-endian dwords, not native C bitfields.
rel2=pp+'hwmgr/ppatomctrl.c';atom=(SRC/rel2).read_text()
helper='''/* The ATOM parameter word is LE: frequency[23:0], flags[31:24].
 * Converting a value before assigning a 24-bit C bitfield truncates it on BE.
 * Read/write the complete parameter word, avoiding native bitfield layout.
 */
static void atomctrl_set_clock_word(void *word, uint32_t clock, uint8_t flags)
{
	put_unaligned_le32((clock & 0x00ffffff) | ((uint32_t)flags << 24), word);
}

static uint32_t atomctrl_clock_word_frequency(const void *word)
{
	return get_unaligned_le32(word) & 0x00ffffff;
}

static uint8_t atomctrl_clock_word_flags(const void *word)
{
	return get_unaligned_le32(word) >> 24;
}

'''
afixed=atom.replace('#include <linux/delay.h>','#include <linux/delay.h>\n#include <linux/unaligned.h>')
afixed=afixed.replace('union voltage_object_info {',helper+'union voltage_object_info {',1)
# All six V4-layout callers in this producer, including the memory timing input.
pairs=[('mpll_parameters.ulClock.ulClock = cpu_to_le32(clock_value);','atomctrl_set_clock_word(&mpll_parameters.ulClock, clock_value, 0);'),
('pll_parameters.ulClock = cpu_to_le32(clock_value);','atomctrl_set_clock_word(&pll_parameters, clock_value, 0);'),
('pll_patameters.ulClock.ulClock = cpu_to_le32(clock_value);\n\tpll_patameters.ulClock.ucPostDiv = COMPUTE_GPUCLK_INPUT_FLAG_SCLK;', 'atomctrl_set_clock_word(&pll_patameters.ulClock, clock_value,\n\t\t\t\tCOMPUTE_GPUCLK_INPUT_FLAG_SCLK);'),
('pll_patameters.ulClock.ulClock = cpu_to_le32(clock_value);\n\tpll_patameters.ulClock.ucPostDiv =\n\t\tCOMPUTE_GPUCLK_INPUT_FLAG_DEFAULT_GPUCLK;', 'atomctrl_set_clock_word(&pll_patameters.ulClock, clock_value,\n\t\t\t\tCOMPUTE_GPUCLK_INPUT_FLAG_DEFAULT_GPUCLK);'),
('le32_to_cpu(mpll_parameters.ulClock.ulClock)','atomctrl_clock_word_frequency(&mpll_parameters.ulClock)'),
('mpll_parameters.ulClock.ucPostDiv','atomctrl_clock_word_flags(&mpll_parameters.ulClock)'),
('le32_to_cpu(pll_parameters.ulClock)','atomctrl_clock_word_frequency(&pll_parameters)'),
('pll_parameters.ucPostDiv','atomctrl_clock_word_flags(&pll_parameters)'),
('le32_to_cpu(pll_patameters.ulClock.ulClock)','atomctrl_clock_word_frequency(&pll_patameters.ulClock)'),
('pll_patameters.ulClock.ucPostDiv','atomctrl_clock_word_flags(&pll_patameters.ulClock)'),
('memory_clock_parameters.asDPMMCReg.ulClock.ulClockFreq =\n\t\tmemory_clock & SET_CLOCK_FREQ_MASK;\n\tmemory_clock_parameters.asDPMMCReg.ulClock.ulComputeClockFlag =\n\t\tADJUST_MC_SETTING_PARAM;', 'atomctrl_set_clock_word(&memory_clock_parameters.asDPMMCReg.ulClock,\n\t\t\t\tmemory_clock & SET_CLOCK_FREQ_MASK,\n\t\t\t\tADJUST_MC_SETTING_PARAM);')]
for old,new in pairs:
    assert old in afixed,old
    afixed=re.sub(r'(?<![A-Za-z0-9_])'+re.escape(old),lambda match:new,afixed)
assert '.ulClock.ulClock =' not in afixed
# Similar variable names in SI full-word callers must remain untouched.
def function(text,name):
    start=text.index('int '+name+'(');return text[start:text.index('\n}\n',start)+3]
assert function(atom,'atomctrl_get_memory_pll_dividers_si')==function(afixed,'atomctrl_get_memory_pll_dividers_si')
assert 'matomctrl' not in afixed
receipt['patches']['0020-atomctrl-serialize-complete-clock-word.patch']=patch('0020-atomctrl-serialize-complete-clock-word.patch',rel2,atom,afixed)
(OUT/'ppatomctrl.fixed.c').write_text(afixed)
# Compiler tests use exact packed struct definitions and literal declarations.
license=original[:original.index('#include')]
preamble=license+'''\ntypedef unsigned char uint8_t;
typedef unsigned short uint16_t;
typedef unsigned int uint32_t;
typedef uint32_t SMU_VoltageLevel;
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#define cpu_to_be32(x) (x)
#define cpu_to_be16(x) (x)
#define cpu_to_le32(x) __builtin_bswap32(x)
#define ATOM_BIG_ENDIAN 1
#else
#define cpu_to_be32(x) __builtin_bswap32(x)
#define cpu_to_be16(x) __builtin_bswap16(x)
#define cpu_to_le32(x) (x)
#define ATOM_BIG_ENDIAN 0
#endif
#pragma pack(push, 1)
'''
structs=''
for n in ['SMU_SclkSetting','SMU74_Discrete_GraphicsLevel','SMU74_Discrete_MemoryLevel']:
    structs+=re.search(r'struct '+n+r' \{.*?\n\};\s*typedef struct '+n+r' '+n+r';',header,re.S).group(0)+'\n'
# SMU74 Graphics has blank line before typedef; use a whitespace-tolerant match.
def declarations(s):
    a=re.search(arr_re,s,re.S).group(0).replace('avfs_graphics_level_polaris10[8]', 'avfs_graphics_level_polaris10[8] __attribute__((used,section(".audit_gfx")))')
    b=re.search(mem_re,s,re.S).group(0).replace('avfs_memory_level_polaris10 =','avfs_memory_level_polaris10 __attribute__((used,section(".audit_mem"))) =')
    vr=re.search(r'vr_config = (.*?);',s).group(1)
    return a+'\n'+b+f'\nconst uint32_t audit_vr __attribute__((used,section(".audit_vr"))) = {vr};\n'
for name,s in [('old',original),('fixed',fixed)]:
    (OUT/(name+'-tables.c')).write_text(preamble+structs+declarations(s))
receipt['field_schemas']={'graphics':gfx_fields,'sclk':sclk_fields,'memory':mem_fields}
receipt['hardware_tested']=False
(OUT/'prepare.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt),flush=True)
