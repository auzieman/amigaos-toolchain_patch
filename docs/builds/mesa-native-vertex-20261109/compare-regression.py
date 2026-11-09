from pathlib import Path
import json,hashlib
b=Path('/srv/data1/tabor-build/linux-live-001/work');w=b/'native-vertex-contract-20261109-001';old=b/'mesa-3d-contracts-20261109-001'
def compare_dirs(a,b):
 results=[]
 for p in sorted(a.glob('upload-*.json')):
  q=b/p.name;assert q.is_file(),q
  x=p.with_suffix('.bin').read_bytes();y=q.with_suffix('.bin').read_bytes()
  same=x==y and json.loads(p.read_text())==json.loads(q.read_text())
  results.append({'file':p.name,'stage':json.loads(p.read_text())['stage'],'same':same,'old_bytes':len(x),'new_bytes':len(y),'old_sha256':hashlib.sha256(x).hexdigest(),'new_sha256':hashlib.sha256(y).hexdigest()})
 assert results
 return results
x86=compare_dirs(old/'buffers-native-rgb-captures',w/'native-vertex-native-rgb-qualified-captures');assert all(r['same'] for r in x86)
off=compare_dirs(old/'offline-spe-captures-009',w/'offline-spe-captures-015');assert all(r['same'] for r in off)
on=compare_dirs(w/'offline-spe-captures-015',w/'offline-spe-captures-016');assert all(r['same']==(r['stage']!=0) for r in on)
point=compare_dirs(old/'offline-spe-captures-008',w/'offline-spe-captures-017');assert all(r['same'] for r in point)
patch=(w/'0012-native-vertex-legacy-xfb-contract.patch').read_text()
paths=[l[6:] for l in patch.splitlines() if l.startswith('+++ b/')]
receipt={'x86_unchanged':x86,'BE_option_off_unchanged':off,'BE_enabled_only_vertex_shader_changes':on,'attribute_free_point_unchanged':point,'source_sha256':{name:hashlib.sha256((w/'mesa-source'/name).read_bytes()).hexdigest() for name in paths},'candidate_libgallium_sha256':hashlib.sha256((w/'offline-spe-output/usr/lib/libgallium-25.0.7.so').read_bytes()).hexdigest(),'limits':'No-op backend cannot execute GPU commands. Shader output comparisons do not establish pixels, XFB GPU execution, or fix the unchanged attribute-free point hang. Native32 legacy-XFB lowering tested separately; arbitrary SSBO producers and lowered64 XFB ordering unqualified.'}
(w/'native-vertex-regression.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS x86/off unchanged; BE enabled VS changes52->160bytes; other RGB stages unchanged; attribute-free point unchanged')
