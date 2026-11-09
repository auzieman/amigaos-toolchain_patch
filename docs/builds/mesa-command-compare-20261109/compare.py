from pathlib import Path
import struct,hashlib,json
w=Path('/srv/data1/tabor-build/linux-live-001/work/mesa-3d-contracts-20261109-001')
a=w/'commands-native-captures';b=w/'offline-spe-captures-007'
files=sorted(a.glob('ib-*-canonical.bin'));assert files
records=[]
for p in files:
 x=p.read_bytes();y=(b/p.name).read_bytes();assert len(x)==len(y) and len(x)%4==0
 xx=struct.unpack('<'+'I'*(len(x)//4),x);yy=struct.unpack('<'+'I'*(len(y)//4),y)
 diffs=[{'dword':i,'x86':v,'spe':z} for i,(v,z) in enumerate(zip(xx,yy)) if v!=z]
 pub=p.name.replace('canonical','published')
 xp=(a/pub).read_bytes();yp=(b/pub).read_bytes()
 assert xp==x
 # Polaris12 profile deliberately does not enable the Polaris11-only opt-in.
 assert yp==b''.join(y[i:i+4][::-1] for i in range(0,len(y),4))
 records.append({'file':p.name,'dwords':len(xx),'differences':diffs,'x86_canonical_sha256':hashlib.sha256(x).hexdigest(),'spe_canonical_sha256':hashlib.sha256(y).hexdigest(),'publication':'x86 native LE; SPE native BE, expected for unchanged Polaris12 selector; no claim of physical LE publication'})
assert len(records)==1 and records[0]['dwords']==400
assert records[0]['differences']==[{'dword':149,'x86':0x28028,'spe':0x2802a}]
# Decode the owning SET_CONTEXT_REG packet rather than treating bit differences
# as an arbitrary expected mask.
assert xx[143]==0xc00e6900 and xx[144]==0x318
register=0x28000+4*(xx[144]+149-145)
assert register==0x28c70 and (xx[149]^yy[149])==2
out={'status':'PASS: construction comparison; GPU execution not tested','records':records,'difference_owner':{'register':hex(register),'name':'CB_COLOR0_INFO','field':'ENDIAN','x86':0,'spe':2,'source':'ac_colorformat_endian_swap returns ENDIAN_8IN32 for COLOR_8_8_8_8 on BE; ac_init_gfx6_cb_surface encodes S_028C70_ENDIAN'},'limits':['Polaris12 upstream no-op profile, not physical Polaris11','one finalized main GFX IB, no chain or preamble exercised','raw SPE published IB intentionally native for this selector; kernel013 opt-in pairing not exercised','no GPU execution, cache visibility or address-translation acceptance']}
(w/'command-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
