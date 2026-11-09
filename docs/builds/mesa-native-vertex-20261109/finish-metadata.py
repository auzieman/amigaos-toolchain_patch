from pathlib import Path
import difflib,json,hashlib,shutil
w=Path('/srv/data1/tabor-build/linux-live-001/work/native-vertex-contract-20261109-001')
p=w/'mesa-source/src/gallium/drivers/radeonsi/si_state.c';s=p.read_text()
a='#include "si_build_pm4.h"';assert s.count(a)==1
n=s.replace(a,a+'\n#include "ac_nir_native_vertex.h"')
a='bool opencode = sscreen->options.vs_fetch_always_opencode;';assert n.count(a)==1
n=n.replace(a,'''/* Native payload decoding also needs complete format metadata in the
       * shader key, including formats that normally need no fetch fixup.
       */
      bool opencode = sscreen->options.vs_fetch_always_opencode ||
                      ac_nir_native_vertex_enabled(sscreen->info.gfx_level);''')
p.write_text(n)
f=w/'0012-native-vertex-legacy-xfb-contract.patch';f.write_text(f.read_text()+''.join(difflib.unified_diff(s.splitlines(True),n.splitlines(True),fromfile='a/src/gallium/drivers/radeonsi/si_state.c',tofile='b/src/gallium/drivers/radeonsi/si_state.c')))
f=w/'native-vertex-source.json';r=json.loads(f.read_text());r['source_sha256']['src/gallium/drivers/radeonsi/si_state.c']=hashlib.sha256(p.read_bytes()).hexdigest();r['metadata_qualification']='Preflight caught forced-open-fetch using omitted ordinary-format metadata; corrected at vertex-element shader-key producer before any deployment.';f.write_text(json.dumps(r,indent=2)+'\n')
for arch in ['spe','native']:
 for suffix in ['build.log','install.log']:
  f=w/('native-vertex-'+arch+'-'+suffix)
  if f.exists():shutil.copy2(f,f.with_name(f.name.replace(suffix,'initial-'+suffix)))
print('Completed producer metadata and shared consumer pairing')
