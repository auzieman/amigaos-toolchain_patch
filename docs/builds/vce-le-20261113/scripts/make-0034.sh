#!/bin/bash
# Generate patch 0034 against the verified 014 tree. /out = private docs/builds/vce-le-20261113 (rw).
set -euo pipefail
A=/work/builds/e2e014/source; T=/work/p0034; rm -rf $T; mkdir -p $T/a $T/b
for f in drivers/gpu/drm/amd/amdgpu/amdgpu_ring.c drivers/gpu/drm/amd/amdgpu/amdgpu_vce.c; do
  mkdir -p $T/a/$(dirname $f) $T/b/$(dirname $f); cp $A/$f $T/a/$f; cp $A/$f $T/b/$f; done
cd $T/b
python3 - <<'EOF'
p='drivers/gpu/drm/amd/amdgpu/amdgpu_ring.c'; s=open(p).read()
old="""		ring->funcs->type == AMDGPU_RING_TYPE_COMPUTE ||
		ring->funcs->type == AMDGPU_RING_TYPE_UVD_ENC);"""
new="""		ring->funcs->type == AMDGPU_RING_TYPE_COMPUTE ||
		ring->funcs->type == AMDGPU_RING_TYPE_UVD_ENC ||
		ring->funcs->type == AMDGPU_RING_TYPE_VCE);"""
assert s.count(old)==1; open(p,'w').write(s.replace(old,new))
p='drivers/gpu/drm/amd/amdgpu/amdgpu_vce.c'; s=open(p).read()
anchor="/**\n * amdgpu_vce_get_create_msg - generate"
helper='''/*
 * Polaris11 big-endian: VCE fetches its ring and IB memory little-endian
 * (VCE_LMI_SWAP_CNTL/1 stay 0), so kernel-built VCE messages are stored LE,
 * matching the ring words written through amdgpu_ring_write().
 */
static void amdgpu_vce_encode_ib(struct amdgpu_ring *ring, struct amdgpu_ib *ib)
{
	unsigned int i;

	if (!amdgpu_ring_uses_sw_le(ring))
		return;
	for (i = 0; i < ib->length_dw; i++)
		ib->ptr[i] = (__force u32)cpu_to_le32(ib->ptr[i]);
}

'''
assert s.count(anchor)==1; i=s.index(anchor)
s=s[:i]+helper+s[i:]
old="\tfor (i = ib->length_dw; i < ib_size_dw; ++i)\n\t\tib->ptr[i] = 0x0;\n"
assert s.count(old)==2, s.count(old)
s=s.replace(old, "\tamdgpu_vce_encode_ib(ring, ib);\n"+old)
open(p,'w').write(s)
EOF
cd $T; diff -ru a b | sed -e 's|^--- a/\([^\t]*\).*|--- a/\1|' -e 's|^+++ b/\([^\t]*\).*|+++ b/\1|' | grep -v '^diff ' > /out/0034-vce-software-little-endian-messages.patch || true
cat /out/0034-vce-software-little-endian-messages.patch; sha256sum /out/0034-vce-software-little-endian-messages.patch
