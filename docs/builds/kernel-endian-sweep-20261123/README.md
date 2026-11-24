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

## ATOM/vbios field sweep (patch 0019-0024 class, 2026-11-24)

Pattern from patches 0019, 0020, 0022 and 0024: vbios/ATOM tables are LE, and their
Hungarian-named fields (`ulXxx`, `usXxx`) are read raw as native values, or written through
native bitfields. `atomscan.py` scans statement by statement for `ul`/`us` reads used as
values without `le16/le32_to_cpu`, the SMC macros or the unaligned helpers. It skips zero
tests (safe either way). The raw hits are in `atomscan-021.txt` (101 hits; most are copies
between already-converted native structs).

Confirmed sites (raw ATOM read, value used natively), Polaris path:

| Site | Field | Effect on BE |
|---|---|---|
| ppatomctrl.c 1588-1606 (`atomctrl_get_leakage_vddc_base_on_leakage`) | `usLeakageBinArrayOffset`, `usElbVDDC*/VDDCI*ArrayOffset`, and the u16 arrays `leakage_bin[]`, `vddc_id_buf[]`, `vddc_buf[]`, `vddci_*` | wrong offsets and leakage voltages: VDDC/VDDCI per DPM level |
| ppatomctrl.c 753, 918 (ASIC profiling) | `ulLoadLineSlop`, `usLkgEuseIndex` | wrong AVFS load line, wrong leakage efuse index |
| ppatomctrl.c 1539, 1557 | `asSVID2Obj.usLoadLine_PSI`, `usVoltageLevel` (atom exec output) | wrong SVI2 load line / virtual voltage id |
| ppatomctrl.c 1663-1666 (`atomctrl_get_edc_hilo_leakage_offset_table`) | `usHiLoLeakageThreshold`, `usEdcDidt{Lo,Hi}Dpm7TableOffset` | wrong EDC leakage table choice (smu7_hwmgr 1482, 2970-2976) |
| process_pptables_v1_0.c 703 | `polaristable->usBoostPowerLimit` | wrong boost power limit (its neighbours are converted) |
| amdgpu_atombios.c 1660-1662 | `ulStartAddrUsedByFirmware`, `usFirmwareUseInKb` | wrong firmware VRAM reservation |

Not reached on Polaris: smu7_hwmgr 3934-3962 (PP_TABLE_V0 state callback), atombios_encoders
2088 (LVDS). Verified converted (false positives): the sclk range table, the AI engine PLL
dividers, the AVFS information copy, and every `amdgpu_atom_*clock_word` call.

Fix: a mechanical `le16_to_cpu`/`le32_to_cpu` at each read (`get_unaligned_le16` for the
u16 arrays reached by vbios offsets), as patch 0040. These are power and clock values
(voltages, limits, VRAM reserve). They are part of the "is the card running at its real
clocks" question, not the glamor fault.
