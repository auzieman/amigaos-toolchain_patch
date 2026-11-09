from pathlib import Path
import difflib,hashlib,json
w=Path('/srv/data1/tabor-build/linux-live-001/work/radeonsi-le-ib-20261109-001');root=w/'mesa-source';patch=''
p=root/'src/gallium/winsys/amdgpu/drm/amdgpu_cs.cpp';s=p.read_text();a='''   for (unsigned i = 0; i < count; i++)
      words[i] = util_cpu_to_le32(words[i]);''';assert s.count(a)==1
n=s.replace(a,'''   uint32_t first = count ? words[0] : 0;
   for (unsigned i = 0; i < count; i++)
      words[i] = util_cpu_to_le32(words[i]);
   fprintf(stderr, "TABOR_IB_SERIALIZED dw=%u first_native=%08x stored_native=%08x\\n",
           count, first, count ? words[0] : 0);''');p.write_text(n);patch+=''.join(difflib.unified_diff(s.splitlines(True),n.splitlines(True),fromfile='a/'+str(p.relative_to(root)),tofile='b/'+str(p.relative_to(root))))
p=root/'src/gallium/drivers/radeonsi/si_clear.c';s=p.read_text();a='''   si_fast_clear(sctx, &buffers, color, depth, stencil);''';assert s.count(a)==1
n=s.replace(a,'''   if (getenv("TABOR_POLARIS11_LE_IB"))
      fprintf(stderr, "TABOR_CLEAR_PATH before_fast=%x\\n", buffers);
'''+a+'''
   if (getenv("TABOR_POLARIS11_LE_IB"))
      fprintf(stderr, "TABOR_CLEAR_PATH after_fast=%x\\n", buffers);''')
a='''   si_fb_clear_via_compute(sctx, &buffers, color);''';assert n.count(a)==1
n=n.replace(a,a+'''
   if (getenv("TABOR_POLARIS11_LE_IB"))
      fprintf(stderr, "TABOR_CLEAR_PATH after_compute=%x\\n", buffers);''');p.write_text(n);patch+=''.join(difflib.unified_diff(s.splitlines(True),n.splitlines(True),fromfile='a/'+str(p.relative_to(root)),tofile='b/'+str(p.relative_to(root))))
(w/'0004-publication-and-clear-path-trace.patch').write_text(patch)
(w/'trace-source-hashes.json').write_text(json.dumps({str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [root/'src/gallium/winsys/amdgpu/drm/amdgpu_cs.cpp',root/'src/gallium/drivers/radeonsi/si_clear.c']},indent=2)+'\n')
