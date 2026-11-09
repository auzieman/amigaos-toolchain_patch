from pathlib import Path
import struct,json,hashlib
w=Path('/srv/data1/tabor-build/linux-live-001/work/mesa-3d-contracts-20261109-001')
results={}
for tag,suffix in [('point','008'),('rgb','009')]:
 a=w/('buffers-native-'+tag+'-captures');b=w/('offline-spe-captures-'+suffix)
 left={p.name:p for p in a.glob('cs-*.bin')};right={p.name:p for p in b.glob('cs-*.bin')}
 assert left and left.keys()==right.keys(), 'Unmatched allocation capture sets'
 entries=[]
 for name,p in sorted(left.items()):
  x=p.read_bytes();y=right[name].read_bytes();assert len(x)==len(y)
  diffs=[i for i in range(0,len(x),4) if x[i:i+4]!=y[i:i+4]]
  entries.append({'file':name,'bytes_compared':len(x),'x86_sha256':hashlib.sha256(x).hexdigest(),'spe_sha256':hashlib.sha256(y).hexdigest(),'differing_dwords':len(diffs),'byte_reversed_dwords':sum(x[i:i+4]==y[i:i+4][::-1] for i in diffs),'first_differences':[{'offset':i,'x86':x[i:i+4].hex(),'spe':y[i:i+4].hex()} for i in diffs[:12]]})
 results[tag]={'capture_count':len(entries),'identical_prefix_count':sum(e['differing_dwords']==0 for e in entries),'entries':entries}
x=(w/'buffers-native-rgb-captures/cs-3-bo-12-size-2097152.bin').read_bytes()[:32]
y=(w/'offline-spe-captures-009/cs-3-bo-12-size-2097152.bin').read_bytes()[:32]
expected=(-1.,-1.,1.,-1.,1.,1.,-1.,1.)
assert struct.unpack('<8f',x)==struct.unpack('>8f',y)==expected
assert all(x[i:i+4]==y[i:i+4][::-1] for i in range(0,32,4))
results['vertex32_evidence']={'expected_native_coordinates':expected,'gpu_LE_interpretation_of_SPE_bytes':struct.unpack('<8f',y),'spe_bytes':y.hex(),'x86_bytes':x.hex(),'scope':'raw CPU-generated RGB vertex payload; paired with source fetch loads lacking explicit endian decode. GPU-generated buffers require a separate producer contract before a shared fetch change.'}
shader_checks=[]
for p in sorted((w/'buffers-native-rgb-captures').glob('upload-*.json')):
 q=w/'offline-spe-captures-009'/p.name
 x=p.with_suffix('.bin').read_bytes();y=q.with_suffix('.bin').read_bytes()
 tail=x[-20:]==bytes.fromhex('00009fbf')*5 and y[-20:]==bytes.fromhex('bf9f0000')*5
 same=x[:-20]==y[:-20] if tail else x==y
 assert same and json.loads(p.read_text())==json.loads(q.read_text())
 shader_checks.append({'file':p.name,'bytes':len(x),'executable_match':same,'UMR_marker_tail_only':tail})
assert len(shader_checks)==4
results['rgb_shader_comparison']=shader_checks
results['limits']=['No GPU execution; Polaris12 no-op profile only','At most first65536bytes per active allocation; snapshots may include unused padding','Point BO9 difference at0x98/0x9c is not classified as a consumed field; no root-cause claim','Native PM4 published on SPE expected because this is not the enabled Polaris11 selector','No driver conversion patch or hardware test from these captures']
(w/'buffer-comparison.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps({t:{k:v for k,v in r.items() if k!='entries'} for t,r in results.items() if t in ['point','rgb']},indent=2))
print('Native32 RGB coordinates mismatch under GPU little-endian interpretation reproduced')
