from pathlib import Path
import difflib,hashlib,json
w=Path('/srv/data1/tabor-build/linux-live-001/work/mesa-3d-contracts-20261109-001')
p=w/'mesa-source/src/gallium/winsys/amdgpu/drm/amdgpu_cs.cpp'
s=p.read_text()
a='/* FENCES */'
helper='''/* Default-off CPU-only offline comparison. Canonical files encode final
 * CPU-constructed numeric words as LE. Published files retain actual bytes.
 * No GPU commands, addresses, or production allocation policy are changed.
 */
static void tabor_capture_ib(const char *dir, unsigned submit, unsigned chunk,
                             const char *phase, const uint32_t *words,
                             unsigned count, bool canonical)
{
   char path[1024];
   snprintf(path, sizeof(path), "%s/ib-%u-chunk-%u-%s.bin", dir, submit, chunk, phase);
   FILE *f = fopen(path, "wb");
   if (!f) {
      fprintf(stderr, "TABOR_IB_CAPTURE failed: %s\\n", path);
      return;
   }
   if (canonical) {
      for (unsigned i = 0; i < count; i++) {
         uint32_t word = util_cpu_to_le32(words[i]);
         fwrite(&word, sizeof(word), 1, f);
      }
   } else {
      fwrite(words, sizeof(*words), count, f);
   }
   fclose(f);
}

'''
assert s.count(a)==1;n=s.replace(a,helper+a)
a='''      if (tabor_explicit_le_gfx_ib(aws, cs->ip_type)) {
         for (unsigned i = 0; i < rcs->num_prev; i++)'''
b='''      const char *capture_dir = cs->ip_type == AMD_IP_GFX ? getenv("TABOR_IB_CAPTURE_DIR") : NULL;
      static unsigned capture_serial;
      unsigned capture_id = 0;
      if (capture_dir) {
         capture_id = p_atomic_inc_return(&capture_serial);
         for (unsigned i = 0; i < rcs->num_prev; i++)
            tabor_capture_ib(capture_dir, capture_id, i, "canonical", rcs->prev[i].buf,
                             rcs->prev[i].cdw, true);
         tabor_capture_ib(capture_dir, capture_id, rcs->num_prev, "canonical",
                          rcs->current.buf, rcs->current.cdw, true);
      }

'''+a
assert n.count(a)==1;n=n.replace(a,b)
a='''      /* Swap command streams. "cst" is going to be submitted. */'''
b='''      if (capture_dir) {
         for (unsigned i = 0; i < rcs->num_prev; i++)
            tabor_capture_ib(capture_dir, capture_id, i, "published", rcs->prev[i].buf,
                             rcs->prev[i].cdw, false);
         tabor_capture_ib(capture_dir, capture_id, rcs->num_prev, "published",
                          rcs->current.buf, rcs->current.cdw, false);
      }

'''+a
assert n.count(a)==1;n=n.replace(a,b)
p.write_text(n)
(w/'0010-offline-command-publication-capture.patch').write_text(''.join(difflib.unified_diff(s.splitlines(True),n.splitlines(True),fromfile='a/src/gallium/winsys/amdgpu/drm/amdgpu_cs.cpp',tofile='b/src/gallium/winsys/amdgpu/drm/amdgpu_cs.cpp')))
(w/'command-capture-source.json').write_text(json.dumps({'before':hashlib.sha256(s.encode()).hexdigest(),'after':hashlib.sha256(n.encode()).hexdigest(),'gpu_execution':False},indent=2)+'\n')
print('Prepared default-off final command publication capture')
