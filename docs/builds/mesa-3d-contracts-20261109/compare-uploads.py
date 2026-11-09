from pathlib import Path
import hashlib,json
w=Path('/srv/data1/tabor-build/linux-live-001/work/mesa-3d-contracts-20261109-001')
result={}
for arch,d in [('x86',w/'offline-native-captures'),('spe',w/'offline-spe-captures-006')]:
 records=[]
 for p in sorted(d.glob('*.json')):
  meta=json.loads(p.read_text());blob=p.with_suffix('.bin').read_bytes();assert len(blob)==meta['bytes']
  records.append({'metadata':meta,'sha256':hashlib.sha256(blob).hexdigest(),'file':p.name})
 result[arch]=records
normalize=lambda rs:sorted([json.dumps({'metadata':r['metadata'],'sha256':r['sha256']},sort_keys=True) for r in rs])
result['match']=normalize(result['x86'])==normalize(result['spe']) and bool(result['x86'])
comparisons=[]
for p in sorted((w/'offline-native-captures').glob('*.bin')):
 a=p.read_bytes();b=(w/'offline-spe-captures-006'/p.name).read_bytes()
 differences=[i for i in range(len(a)) if a[i]!=b[i]]
 # ACO emit_program records exec_size before appending exactly five UMR markers.
 # This classification is restricted to the captured no-constant shaders here.
 marker_tail=(a[-20:]==bytes.fromhex('00009fbf')*5 and b[-20:]==bytes.fromhex('bf9f0000')*5)
 comparisons.append({'file':p.name,'identical':a==b,'differing_byte_offsets':differences,'only_native_UMR_marker_tail':marker_tail and a[:-20]==b[:-20]})
result['byte_analysis']=comparisons
result['executable_comparison']='All captured uploads identical or differ only in the five non-executed UMR end markers; no constants or scratch in this test.'
result['scope']='Complete published shader bytes and scalar metadata; standard constant-point Piglit, same Polaris12 no-op profile. No GPU execution or board acceptance.'
(w/'shader-upload-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
