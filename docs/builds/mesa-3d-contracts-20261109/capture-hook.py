from pathlib import Path
import difflib,hashlib,json
w=Path('/srv/data1/tabor-build/linux-live-001/work/mesa-3d-contracts-20261109-001');p=w/'mesa-source/src/gallium/drivers/radeonsi/si_shader.c';s=p.read_text();a='''   if (sscreen->debug_flags & DBG(SQTT)) {
      /* Remember the uploaded code */''';assert s.count(a)==1
n=s.replace(a,'''   /* CPU-only offline qualification. The no-op DRM backend executes no GPU
    * commands; retain exact publication bytes and native scalar metadata.
    */
   const char *capture_dir = getenv("TABOR_SHADER_CAPTURE_DIR");
   if (capture_dir && shader->binary.type == SI_SHADER_BINARY_RAW) {
      static unsigned capture_serial;
      unsigned serial = p_atomic_inc_return(&capture_serial);
      int stage = shader->selector ? shader->selector->stage : -1;
      char path[1024];
      snprintf(path, sizeof(path), "%s/upload-%u-stage-%d.bin", capture_dir, serial, stage);
      FILE *capture = fopen(path, "wb");
      if (capture) {
         fwrite(code, 1, code_size, capture);
         fclose(capture);
         snprintf(path, sizeof(path), "%s/upload-%u-stage-%d.json", capture_dir, serial, stage);
         capture = fopen(path, "w");
         if (capture) {
            fprintf(capture, "{\\"stage\\":%d,\\"bytes\\":%u,\\"sgprs\\":%u,\\"vgprs\\":%u,\\"float_mode\\":%u,\\"lds_size\\":%u,\\"scratch_bytes_per_wave\\":%u}\\n",
                    stage, code_size, shader->config.num_sgprs, shader->config.num_vgprs,
                    shader->config.float_mode, shader->config.lds_size,
                    shader->config.scratch_bytes_per_wave);
            fclose(capture);
         }
      } else {
         fprintf(stderr, "TABOR_SHADER_CAPTURE failed: %s\\n", path);
      }
   }

'''+a)
p.write_text(n);(w/'0009-offline-shader-publication-capture.patch').write_text(''.join(difflib.unified_diff(s.splitlines(True),n.splitlines(True),fromfile='a/src/gallium/drivers/radeonsi/si_shader.c',tofile='b/src/gallium/drivers/radeonsi/si_shader.c')));print('Prepared default-off CPU-only upload capture')
