# amdgpu endian sweep with sparse (kernel 021 tree, 2026-11-23)

## Method

`sparse-amd.sh` runs sparse 0.6.4 (`C=2`, `-D__CHECK_ENDIAN__ -Wbitwise`,
`-fmax-warnings=100000`) over `drivers/gpu/drm/amd/amdgpu/` in a hard-linked scratch copy of
the 021 source, built with 021's config. Two scratch-only edits; the 021 build tree is
unchanged:

1. `amdgv_sriovmsg.h`: the SR-IOV `_Static_assert`s are skipped under `__CHECKER__`. Sparse
   gets those struct sizes wrong on ppc32, and once it reports an error it stops printing
   warnings. Without this edit, the first runs came out "clean" while printing nothing.
2. GPU-shared memory re-typed from `u32` to `__le32`: `wb.wb`, `ib->ptr`, `fence_drv.cpu_addr`,
   `ring->ring`, `rptr/wptr/trail_fence/cond_exe_cpu_addr`, and the IH `ring/wptr_cpu/rptr_cpu`.

Why the second edit: amdgpu declares GPU-shared memory as plain `u32`, so a plain sparse run
only flags the code that does convert, and the missing conversions stay invisible (3,293
"endian" warnings, almost all on correct `le32_to_cpu` sites). With the types re-annotated,
correct sites go quiet and raw native accesses show up. `sparse-le-by-file.txt` lists the
hits per file.

## Polaris11 path (VI/GFX8/SDMA3/GMC8/DCE11/UVD6/VCE3, kernel 016 chain)

| Site | Class | Status |
|---|---|---|
| `amdgpu_ring_encode_dw` users (ring.h 394-481), `is_le` IB accessors (ring.h 504/512) | 016-chain software-LE encoder | correct, sparse flags only the u32 return type |
| gfx_v8 clear-state buffer (1298-1330), wb write 4415 | explicit `cpu_to_le32` into a u32 parameter | correct |
| sdma_v3 ring tests, VM PTE copy/write/set, TTM copy/fill (879-1018, 1634-1663); sdma rptr/wptr reads | native packets | correct: SDMA v3 sets RB/IB/RPTR-writeback swap enables under `__BIG_ENDIAN` |
| gfx_v8 EDC GPR workaround IB (1614-1698) | native IB words | Carrizo only, not reached on Polaris |
| gfx_v8 `get_rptr`/`get_wptr` (6309, 6320, 6535) | raw read of writeback slots that `set_wptr` writes encoded on software-LE rings | **gap**: the readback is byte-swapped. Diagnostics and reset paths, not flow control |
| `amdgpu_ring_generic_pad_ib` (ring.c 128), `memset32(ib->ptr, nop)` (gfx.c 1461) | native NOP into an IB | **latent gap**: only user IBs (cs.c 423, padded by Mesa) and the gfx IB test are `is_le` today |
| `amdgpu_kiq_rreg` (gfx.c 1098) | raw read of a GPU-written wb slot | gap, SR-IOV path |
| tonga_ih `set_rptr` (279) | native write of an IH shadow rptr | low; the GPU takes rptr from the doorbell/register write |
| UVD/VCE/VCN (amdgpu_uvd/vce/vcn, uvd_v6) | native message/IB words | not reviewed yet; 016 patch 0034 covers VCE messages |

Conclusion: the 016 chain keeps the live Polaris kernel path consistent. The glamor fault is
on the Mesa side. Next kernel candidates for re-typing are the MQDs (`vi_mqd`), CPU-updated
page tables (`amdgpu_vm_cpu`) and the firmware/atom table structs.
