from pathlib import Path
import difflib,json,hashlib
w=Path('/srv/data1/tabor-build/linux-live-001/work/native-vertex-contract-20261109-001')
p=w/'mesa-source/src/gallium/drivers/radeonsi/si_get.c';s=p.read_text()
a='#include "si_pipe.h"'
# Use the existing first project include as a stable insertion point.
a=next(l for l in s.splitlines() if l.startswith('#include "si_'))
n=s.replace(a,a+'\n#include "ac_nir_native_vertex.h"',1)
a='caps->draw_vertex_state = !(sscreen->debug_flags & DBG(NO_FAST_DISPLAY_LIST));';assert n.count(a)==1
n=n.replace(a,'''/* The display-list fast path requires fix_fetch_always == 0. Keep
    * native vertex decoding on the normal path, which carries its format key.
    */
   caps->draw_vertex_state = !(sscreen->debug_flags & DBG(NO_FAST_DISPLAY_LIST)) &&
                             !ac_nir_native_vertex_enabled(sscreen->info.gfx_level);''')
p.write_text(n)
f=w/'0012-native-vertex-legacy-xfb-contract.patch';f.write_text(f.read_text()+''.join(difflib.unified_diff(s.splitlines(True),n.splitlines(True),fromfile='a/src/gallium/drivers/radeonsi/si_get.c',tofile='b/src/gallium/drivers/radeonsi/si_get.c')))
f=w/'native-vertex-source.json';r=json.loads(f.read_text());r['source_sha256']['src/gallium/drivers/radeonsi/si_get.c']=hashlib.sha256(p.read_bytes()).hexdigest();r['fastpath']='Optional draw_vertex_state capability withheld only for native-payload opt-in: its upstream assertion excludes fetch fixups. Normal draw path retained.';f.write_text(json.dumps(r,indent=2)+'\n')
print('Guarded incompatible optional display-list fast path')
