from pathlib import Path
import json,hashlib
root=Path('/srv/data1/tabor-build/linux-live-001/work/radeonsi-systemic-20261109-001/mesa-source');w=root.parent.parent/'mesa-systemic-boundaries-20261109-001'
cs='src/gallium/winsys/amdgpu/drm/amdgpu_cs.cpp';si='src/gallium/drivers/radeonsi/'
entries=[
('PM4 construction','src/gallium/include/winsys/radeon_winsys.h','cs->current.buf[cs->current.cdw++] = value','CPU native; retain until publication','source confirmed'),
('GFX publication',cs,'tabor_serialize_gfx_ib(rcs->current.buf','native32 to GPU LE32 after all fixups','physically traced; shaderless write accepted'),
('GFX chains',cs,'tabor_serialize_gfx_ib(rcs->prev[i].buf','same conversion for all finalized chunks','offline byte checks; physical chain coverage open'),
('Preamble',cs,'tabor_serialize_gfx_ib(map, preamble_num_dw)','serialize once after padding','offline checks; preemption physical coverage open'),
('Shader executable',si+'si_shader.c','exec[j] = util_cpu_to_le32(exec[j])','ACO native executable words to LE after relocation','offline upload checks; shader execution open'),
('Compiler GPU mode','src/amd/compiler/aco_ir.h','struct float_mode','packed GPU mode must be CPU-independent before serialization','old BE defect reproduced all256 settings; candidate fixed'),
('Compiler mode producer','src/amd/compiler/aco_instruction_selection.cpp','config->float_mode =','shared float_mode.val becomes config numeric GPU mode','source confirmed; connected build candidate'),
('Shader mode register',si+'si_state_shaders.cpp','S_00B128_FLOAT_MODE(shader->config.float_mode)','numeric mode inserted into PS register then PM4 serialized','source confirmed; physical acceptance open'),
('Descriptors',si+'si_descriptors.c','util_memcpy_cpu_to_le32(ptr,','native descriptor words serialized by existing helper','existing conversion; do not double-swap'),
('Constant buffers',si+'si_descriptors.c','util_memcpy_cpu_to_le32(tmp, ptr, size)','native CPU constants serialized by existing helper','existing conversion; indirect paths need qualification'),
('Blitter vertices',si+'si_state_draw.cpp','Blits don\'t use vertex buffers.','clear rectangle uses native scalar user-SGPR packet data','exclude ordinary vertex upload for this clear'),
('General vertex buffers',si+'si_state_draw.cpp','void si_set_vertex_buffer_descriptor','typed/raw vertex data distinct from LE descriptor words','open; no blanket raw BO swap'),
('Color surface layout','src/amd/common/ac_formats.c','ac_colorformat_endian_swap(uint32_t colorformat)','existing format-specific hardware endian selection','source confirmed; preserve typed policy'),
('Readback staging',si+'si_texture.c','static void *si_texture_transfer_map','tiled VRAM readback stages into linear CPU mapping','open connected shader/copy/map validation'),
('Raw buffer mapping',si+'si_buffer.c','static void *si_buffer_transfer_map','byte mapping is not universally numeric conversion','open typed consumer audit'),
('Completion response',cs,'util_le64_to_cpu(*user_fence_cpu)','GPU LE64 fence to native comparison','8192cases/arch pass; physical clear still zero'),
('Userqueue response','src/gallium/winsys/amdgpu/drm/amdgpu_userq.h','__next_wptr - *userq->user_fence_ptr','native dereference of GPU fence requires endian review','not active on6.12 kernel queue; unresolved'),
('Compiler bit helpers','src/amd/compiler/aco_util.h','storage |= data_type(value & mask) << offset','explicit numeric shifts independent of memory byte order','source confirmed; not all C++ bitfields are unsafe')]
result=[]
for name,path,anchor,contract,state in entries:
 p=root/path;s=p.read_text();lines=s.splitlines();hits=[i for i,line in enumerate(lines) if anchor in line];assert hits,(name,path,anchor)
 result.append({'boundary':name,'path':path,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'contract':contract,'state':state,'anchors':[{'line':i+1,'excerpt':'\n'.join(lines[max(0,i-2):i+3])} for i in hits[:8]]})
(w/'boundary-ledger.json').write_text(json.dumps({'scope':'Pinned active RadeonSI/ACO clear + general workstation data paths; source anchors are not complete coverage or hardware acceptance','boundaries':result},indent=2)+'\n');print('retained',len(result),'source-anchored boundaries; not a completeness claim')
