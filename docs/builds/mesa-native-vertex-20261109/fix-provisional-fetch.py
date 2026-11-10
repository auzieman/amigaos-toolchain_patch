from pathlib import Path
import difflib
w=Path('/srv/data1/tabor-build/linux-live-001/work/f2f-contract-20261109-001/mesa-source/src/gallium/drivers/radeonsi')
p=w/'si_nir_lower_vs_inputs.c';s=p.read_text();old='   if (ac_nir_native_vertex_enabled(sel->screen->info.gfx_level) || opencode ||';assert s.count(old)==1
p.write_text(s.replace(old,'   if (opencode ||'))
print('Removed global bypass of format-key ownership; keyed opencode retained.')
