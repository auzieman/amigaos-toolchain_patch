#!/bin/bash
# Generate patch 0035 against the verified 015 tree. /out = private docs/builds/compute-le-20261114 (rw).
set -euo pipefail
A=/work/builds/e2e015/source; T=/work/p0035; rm -rf $T; mkdir -p $T/a $T/b
f=drivers/gpu/drm/amd/amdgpu/amdgpu_cs.c
mkdir -p $T/a/$(dirname $f) $T/b/$(dirname $f); cp $A/$f $T/a/$f; cp $A/$f $T/b/$f
cd $T/b
python3 - <<'PY'
p='drivers/gpu/drm/amd/amdgpu/amdgpu_cs.c'; s=open(p).read()
old="""	if (amdgpu_polaris11_le_user_ib &&
	    p->adev->asic_type == CHIP_POLARIS11 &&
	    ring->funcs->type == AMDGPU_RING_TYPE_GFX)
		ib->is_le = true;"""
new="""	if (amdgpu_polaris11_le_user_ib &&
	    p->adev->asic_type == CHIP_POLARIS11 &&
	    (ring->funcs->type == AMDGPU_RING_TYPE_GFX ||
	     ring->funcs->type == AMDGPU_RING_TYPE_COMPUTE))
		ib->is_le = true;"""
assert s.count(old)==1; open(p,'w').write(s.replace(old,new))
PY
cd $T; diff -ru a b | sed -e 's|^--- a/\([^\t]*\).*|--- a/\1|' -e 's|^+++ b/\([^\t]*\).*|+++ b/\1|' | grep -v '^diff ' > /out/0035-amdgpu_cs-hunk.patch || true
cat /out/0035-amdgpu_cs-hunk.patch; sha256sum /out/0035-amdgpu_cs-hunk.patch
