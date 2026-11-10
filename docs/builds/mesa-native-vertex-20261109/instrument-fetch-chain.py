from pathlib import Path
w=Path('/srv/data1/tabor-build/linux-live-001/work/f2f-contract-20261109-001/mesa-source/src/gallium/drivers/radeonsi')
changes={
'si_state.c':('      if (always_fix || check_alignment || opencode)\n         v->fix_fetch[i] = fix_fetch.bits;', '      if (ac_nir_native_vertex_enabled(sscreen->info.gfx_level))\n         fprintf(stderr, "TABOR_FETCH_PRODUCER i=%u format=%u channel_bits=%u bits=%02x log=%u channels=%u kind=%u\\n", i, elements[i].src_format, channel->size, fix_fetch.bits, fix_fetch.u.log_size, fix_fetch.u.num_channels_m1+1, fix_fetch.u.format);\n      if (always_fix || check_alignment || opencode)\n         v->fix_fetch[i] = fix_fetch.bits;'),
'si_state_shaders.cpp':('      key->ge.mono.vs_fix_fetch[i].bits = fix_fetch;', '      key->ge.mono.vs_fix_fetch[i].bits = fix_fetch;\n      fprintf(stderr, "TABOR_FETCH_KEY i=%u raw=%02x log=%u kind=%u\\n", i, fix_fetch, key->ge.mono.vs_fix_fetch[i].u.log_size, key->ge.mono.vs_fix_fetch[i].u.format);'),
'si_nir_lower_vs_inputs.c':('   unsigned log_size = fix_fetch.u.log_size;', '   unsigned log_size = fix_fetch.u.log_size;\n   fprintf(stderr, "TABOR_FETCH_CONSUMER raw=%02x log=%u channels=%u kind=%u\\n", fix_fetch.bits, log_size, fix_fetch.u.num_channels_m1+1, fix_fetch.u.format);')}
for n,(old,new) in changes.items():
 p=w/n;s=p.read_text();assert s.count(old)==1,(n,s.count(old));p.write_text(s.replace(old,new))
