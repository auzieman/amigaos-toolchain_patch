from pathlib import Path
import difflib,hashlib,json
w=Path('/srv/data1/tabor-build/linux-live-001/work/mesa-3d-contracts-20261109-001');root=w/'mesa-source';patch='';receipts={}
p=root/'src/gallium/drivers/radeonsi/si_state_draw.cpp';s=p.read_text();a='''         sctx->vertex_buffers_dirty = false;
      }
   }

   return true;''';assert s.count(a)==1
block='''      /* Inline descriptors remain native PM4 payload until CS publication.
       * Only the separate shader-fetched descriptor table is GPU LE memory.
       * Both normal draw and draw_vertex_state writers converge here.
       */
      if (alloc_size) {
         unsigned num_dw = (count - count_in_user_sgprs) * 4;
         for (unsigned dw = 0; dw < num_dw; dw++)
            ptr[dw] = util_cpu_to_le32(ptr[dw]);
      }
'''
n=s.replace(a,'''         sctx->vertex_buffers_dirty = false;
      }
'''+block+'''   }

   return true;''');p.write_text(n);patch+=''.join(difflib.unified_diff(s.splitlines(True),n.splitlines(True),fromfile='a/'+str(p.relative_to(root)),tofile='b/'+str(p.relative_to(root))));receipts[str(p.relative_to(root))]={'before':hashlib.sha256(s.encode()).hexdigest(),'after':hashlib.sha256(n.encode()).hexdigest()};(w/'vertex-publication-block.txt').write_text(block)
p=root/'src/gallium/drivers/radeonsi/si_state.c';s=p.read_text();a='memcpy(map, divisor_factors, num_divisors * sizeof(divisor_factors[0]));';assert s.count(a)==1;n=s.replace(a,'util_memcpy_cpu_to_le32(map, divisor_factors, num_divisors * sizeof(divisor_factors[0]));');p.write_text(n);patch+=''.join(difflib.unified_diff(s.splitlines(True),n.splitlines(True),fromfile='a/'+str(p.relative_to(root)),tofile='b/'+str(p.relative_to(root))));receipts[str(p.relative_to(root))]={'before':hashlib.sha256(s.encode()).hexdigest(),'after':hashlib.sha256(n.encode()).hexdigest()}
(w/'0008-radeonsi-publish-vertex-metadata-le.patch').write_text(patch);(w/'vertex-metadata-source.json').write_text(json.dumps({'files':receipts,'patch_sha256':hashlib.sha256(patch.encode()).hexdigest(),'scope':'GPU-fetched VB descriptor tables and four-word instance divisor factors; CPU cached descriptors and inline PM4 remain native','hardware_tested':False},indent=2)+'\n');print('Patched converged vertex metadata publication boundaries')
