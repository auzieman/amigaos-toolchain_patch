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

### Patch 0040: build result (2026-11-24)

`patches/linux/experiments/0040-atom-table-field-byte-order.patch` covers every site in the
table above, plus two more:
- ppatomctrl.c 1203 (`atomctrl_get_voltage_evv`): `usVoltageLevel` was stored raw into the
  GetVoltageInfo parameter space. Its sibling at 1157 uses `cpu_to_le16`.
- atom.c 1551: `ctx->version` from `ulFirmwareRevision` (coredump print only).

On the R730 the patch went into a hardlinked copy of the 021 tree (`source-0040`, with build
output in `out-0040`) and was built with the kernel image (`powerpc-linux-gnu-`, the 021
`.config`, `make drivers/gpu/drm/amd/amdgpu/`). The build exits 0 with no warnings and
no errors. The patch has not been run on the board yet.

### Encode side: `atomscan.py --write`

`--write` flags stores into `ul`/`us` fields from a non-constant value with no `cpu_to_le*` in
the statement. Over amdgpu + pm + DC bios it gives 83 hits. Polaris-reachable triage:
- Native driver structs (`hwmgr->thermal_controller`, `cac_dtp_table`, `avfs_params`, which go
  to the SMC through `PP_HOST_TO_SMC_*`): fine.
- ppatomctrl.c 794-900 `usEfuseIndex = sXxx_fuse.usEfuseIndex`: an LE-to-LE copy, fine.
- ppatomctrl.c 1203: a real bug, now in 0040.
- The rest are Vega/atomfirmware (`ppatomfwctrl.c`, `vega*_processpptables.c`), which Polaris
  does not run.

Multi-byte ATOM bitfields (`ULONG x:24`, `USHORT x:1`) on the legacy path all go through
whole-word helpers (`amdgpu_atom_set_clock_word`, `le16_to_cpu(usEncoderCap)`,
`ulDispEngClkFreq = cpu_to_le32(crtc << 24 | clk)`). The legacy path is clean.

### DC (display core): the same class, inactive

The 021 config has `CONFIG_DRM_AMD_DC` off, so the board runs `dce_v11_0` + `atombios_*.c`.
DC has the same missing-LE pattern. Fix these if DC is ever enabled:
- command_table.c 327-363 `encoder_control_digx_v5`: `ulPixelClock` stored raw. v3/v4
  convert.
- command_table.c 890-915 `transmitter_control_v1_6`: `ulSymClock` (32-bit) stored raw,
  then scaled with `le16` helpers.
- command_table.c 1149/1168 `set_pixel_clock_v6`: `cpu_to_le32` into the
  `ulPixelClock:24` bitfield. The fix is `amdgpu_atom_set_clock_word` (patch 0020/0022 class).
- bios_parser.c 1556-1559: `usHBR2En`/`usHDMI6GEn`/`usHBR3En` read as BE bitfields of the LE
  `usEncoderCap`. These read bits 9-11, which disables DP HBR2 and HDMI 6G. The legacy
  path does `le16_to_cpu(usEncoderCap)`.
- bios_parser.c 2966 `usMasterDataTableOffset`, 2766-2809 bracket-layout offsets and ids,
  1262 panel mm size: raw reads.

### Re-review of 0040 and pass 2 (2026-11-24)

**Corrected in 0040:**
- Reverted the `usLkgEuseIndex` hunk. `sInput_FuseValues` is the LE *input* to the
  ReadEfuseValue command table, so the raw VBIOS-to-param copy was already correct (like the
  other six efuse copies). The read scan cannot see that the destination is an ATOM parameter.
  Triage rule: an ATOM field copied into an ATOM parameter stays raw. An ATOM field read into
  driver state is decoded.

**Added to 0040:**
- ppatomctrl.c `atomctrl_get_edc_leakage_table`: `DIDT_REG[]` was copied raw from the VBIOS,
  then written to the DIDT registers by `smu7_program_edc_didt_registers`. Now `le32_to_cpu`.
  The name scan missed it because the field is not Hungarian (found by `biosptr.py`).
- atom.c `usMasterDataTableOffset` / `ListOfDataTables.FirmwareInfo`: raw offsets that lead to
  the `ulFirmwareRevision` read. The whole chain is now decoded.

**Not the endian class:** `get_edc_leakage_table` adds `offset` to `table_address` but returns
`temp` (the GFX_Info base). This is an upstream logic bug and is left as is.

**New scanner, `biosptr.py`:** taints pointers that come from a VBIOS source
(`smu_atom_get_data_table`, `ctx->bios +`, `GET_IMAGE`, `CSTR`) and ATOM-typed
parameters and locals. It flags any multi-byte field or index read through them without an LE helper.
Over the Polaris powerplay and legacy display files it gives 69 hits. Everything left over is a zero
test, a byte field, address-of, v0-only `processpptables.c`, or atom.c's own context struct.
The VBIOS side is closed for Polaris.

### Pass 2: kernel CPU accesses to GPU-visible memory (patch 0041)

Contract:
- Kernel IBs default to `is_le=false` and are fetched by CP with `INDIRECT_BUFFER` swap=2,
  so native `ib->ptr[]` is correct for gfx/compute kernel IBs.
- SDMA v3 has hardware swap.
- User IBs are `is_le=true`, and `amdgpu_ib_get/set_value` honour that.
- VCE encodes kernel IBs (`amdgpu_vce_encode_ib`).

The grep of `ptr[]/cpu_addr[]/msg[]/wb[]` accesses without helpers over 39 Polaris files gives
198 hits, almost all IB building under that contract. Two real gaps:
- **amdgpu_uvd.c message parser:** `msg[1]` (type), `msg[2]` (handle), and the width, height,
  dpb, pitch and `msg[61]` fields were read raw. The UVD message is LE: the kernel's own create
  message uses `cpu_to_le32`, MP_SWAP_CNTL is 0, and `msg[59]` is already decoded. On BE a
  decode message (type 1) reads as 0x01000000 and is rejected as an illegal type, and handles
  are stored swapped (the kernel destroy message then names the wrong handle). Now
  `le32_to_cpu`.
- **uvd_v6_0.c encoder create/destroy IBs:** patch 0023 made the UVD_ENC *ring* software LE,
  but the kernel-built encoder IBs stayed native. The 0023 README calls this out ("referenced
  IB payloads are separate objects") and leaves IB execution open. Added
  `uvd_v6_0_enc_encode_ib`, mirroring VCE.

The 0040 and 0041 tree builds clean (exit 0, no warnings).

Checked clean:
- Firmware header and ucode parsing (gfx/SDMA/UVD/VCE/MC/SMU)
- the MQD publish (`writel`)
- the VM SDMA PTEs (`__le64`)
- the UVD decode CS parser (`amdgpu_ib_get_value`)

`amdgpu_ucode_hdr_version` compares u16 LE fields raw, but only gfx11 calls it (not Polaris).

### Upstream and AMD DKMS comparison (2026-11-24)

References on the R730 in /home/owner/upstream:
- mainline through v7.4-rc4: a sparse clone of drivers/gpu/drm/amd;
- AMD amdgpu-dkms 7.2.3-2428518 (repo.radeon.com).

**Post-IB compute path:** `gfx_v8_0_ring_emit_fence_compute`, `_emit_pipeline_sync` and
`_emit_vm_flush` are identical in 021 and DKMS. `_emit_ib_compute` differs only in our `is_le`
swap select. HDP flush is refactored, with the same packets. Of the 256 mainline commits since
v6.12 on the GFX8 and shared scheduling files, none fixes a fence or ring packet running under
a user VMID.

**Backported as 0042:** mainline 63a59637517 (`amdgpu_cs_patch_ibs` ignored the mapping
`offset_in_bo` for CPU-parsed rings: UVD and VCE here). It builds clean.

Reviewed, not applicable:
- 566ed98e48b (TLB-invalidate fence across combined unmap/map): user-VM faults, but no VMID
  mis-tagging;
- 91cf34bc5a5 (MQD fairness);
- 6e54e467973 (compute COND_EXEC for soft reset);
- cb1e657ccac, 0e4ef0ead60, 47cd3118509 (fence and flush refactor follow-ups).

### Sweep of the files our series never touched (2026-11-24)

Upstream is LE-only, so "unchanged from upstream" means "never BE-checked", not "verified".
The VM page-table oracle shows it: vanilla `amdgpu_vm_sdma.c` byte-reverses every GTT PTE on
ppc. Direct GPU-word accesses in the unchanged files (fence, IH, irq, gmc_v8, gmc, sdma_v3, vi,
vm, ids, job, gfx, gart, device) give 86 sites:
- **Already LE upstream:** the fence read, IH wptr/IV decode (tonga_ih, amdgpu_ih), SDMA
  rptr/wptr (hardware RB/rptr swap), the GART PTE `writeq` and the SDMA ring-test wb.
- **Latent gaps, now patch 0043:** the `amdgpu_kiq_rreg` wb read (raw) and the SDMA
  `use_pollmem` wptr poll without SWAP_ENABLE. Both are SR-IOV/VF paths, not reached here.
  It builds clean.

**Hardware swap-control inventory** (every `*SWAP*`/`*ENDIAN*` field of GFX8 CP and RLC in
gfx_8_0_sh_mask.h):
- `CP_RB0_CNTL.BUF_SWAP`, `CP_HQD_PQ_CONTROL.ENDIAN_SWAP` and the IB swap bits follow our
  software-LE policy.
- `CP_ENDIAN_SWAP` is written 0.
- `CP_RB*_RPTR_ADDR.RB_RPTR_SWAP` is 0 (the low address bits), so rptr is written LE, matching
  the LE decode.
- `CP_DMA_*_COMMAND` SRC/DST_SWAP come from the user's DMA_DATA (Mesa: 0).
- The semaphore swap fields are unused.
- **`RLC_MC_CNTL.RDREQ_SWAP/WRREQ_SWAP` are never programmed on GFX8** (gfx6 and gfx7 write 0).
  Read the register on the board.
