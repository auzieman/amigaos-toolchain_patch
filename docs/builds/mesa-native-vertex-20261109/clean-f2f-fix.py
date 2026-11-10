from pathlib import Path
import difflib,json,hashlib
base=Path('/srv/data1/tabor-build/linux-live-001/work');w=base/'f2f-contract-20261109-001';parent=base/'native-vertex-contract-20261109-001'
# Reconstruct a clean candidate from original files, retaining only the fix.
files=['src/amd/compiler/aco_instruction_selection.cpp','src/gallium/drivers/radeonsi/si_state.c','src/gallium/drivers/radeonsi/si_state_shaders.cpp','src/gallium/drivers/radeonsi/si_nir_lower_vs_inputs.c']
patch=[];hashes={}
for rel in files:
 original=(parent/'mesa-source'/rel).read_text();clean=original
 if rel.endswith('si_nir_lower_vs_inputs.c'):
  old='   if (ac_nir_native_vertex_enabled(sel->screen->info.gfx_level) || opencode ||';assert clean.count(old)==1
  clean=clean.replace(old,'   /* The producer records native fetch conversion in the populated shader key.\n    * Provisional variants have no format metadata and must keep typed loads.\n    */\n   if (opencode ||')
 (w/'mesa-source'/rel).write_text(clean)
 if clean!=original:
  patch+=list(difflib.unified_diff(original.splitlines(True),clean.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
 hashes[rel]=hashlib.sha256(clean.encode()).hexdigest()
(w/'fix-provisional-format.patch').write_text(''.join(patch));(w/'fix-source.json').write_text(json.dumps(hashes,indent=2)+'\n');print('Clean candidate: only shader-key ownership fix retained.')
