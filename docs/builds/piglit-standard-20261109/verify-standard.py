from pathlib import Path
import tarfile,json,hashlib
w=Path('/srv/data1/tabor-build/linux-live-001/work/piglit-standard-20261109-001');receipt=json.loads((w/'intake.json').read_text());orig=next(x['file'] for x in receipt['sources']['piglit']['files'] if '.orig.tar.' in x['file'])
paths=['tests/spec/glsl-es-1.00/execution/sanity.shader_test','tests/spec/glsl-es-1.00/execution/glsl-no-vertex-attribs.shader_test','tests/spec/gles-2.0/minmax.c','tests/shaders/shader_runner.c','tests/util/piglit-util-gl.c','tests/util/piglit-framework-gl/piglit_fbo_framework.c']
found={}
with tarfile.open(orig) as t:
 for m in t:
  match=next((p for p in paths if m.name==p or m.name.endswith('/'+p)),None)
  if match:
   data=t.extractfile(m).read();assert data==(w/'piglit'/match).read_bytes();found[match]=hashlib.sha256(data).hexdigest()
assert len(found)==len(paths)
(w/'unmodified-test-inputs.json').write_text(json.dumps({'status':'PASS','files_match_verified_upstream_orig_archive':found,'local_test_modifications':False,'debian_source_version':receipt['sources']['piglit']['version']},indent=2)+'\n');print('Standard tests and core framework match verified upstream source archive.')
