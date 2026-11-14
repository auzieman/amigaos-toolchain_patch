# Kernel016: compute user IBs little-endian, second-board confirmation of 0035

Second A1222 (Polaris11 1002:67ff rev 0xff, subsystem 1002:0b04, 10 CUs), same rescue
stick as [vce-le-20261113](../vce-le-20261113/README.md). This record independently
confirms the kernel half of
[0035-kernel-compute-user-ib-software-le.patch](../../../patches/mesa/polaris-be-20261113/0035-kernel-compute-user-ib-software-le.patch)
on a second board, with a different user-space Mesa build. It also gives a wave-level
diagnosis of why the change is needed. It is not a second fix:
`0035-amdgpu_cs-hunk.patch` is byte-identical to the `amdgpu_cs.c` hunk of that patch.
It omits only the `amdgpu_drv.c` parameter-description text.

## User space

The user-space Mesa build is separate and not part of this repository: Mesa 26.2.3,
radeonsi + ACO, no LLVM. It is a contributor's own big-endian port. GPU-visible data is
built little-endian: IBs are converted at flush, shader code at upload, and CB ENDIAN is
NONE. Application buffers stay host order and are swapped in the shader. It installs
under `/opt/a1222-gl` with its own glibc. The test is `scripts/gltest.c`: surfaceless
EGL, GLES2, one 64x64 RGBA8 FBO, a glClear stage and a two-triangle VBO draw stage.
Each stage reads back all 4096 pixels. The trial driver is `scripts/trial-gl.sh`; it
samples GRBM/CP registers every second and runs `scripts/wavedump` (debugfs
`amdgpu_wave`/`amdgpu_gpr`) at +3 s and +5 s.

## Failure on kernel015 (hardware-015-002), 2026-11-14

Fresh power-cycle boot, root RO, `modprobe amdgpu polaris11_le_user_ib=1` (reads back
Y). Packet-only `gfx-write le` passes in GTT, VRAM and USWC. `gltest clear` gives
`ring gfx timeout, but soft recovered`; 4096/4096 pixels read back zero; no VM fault.
An earlier boot with `cg_mask=0 ppfeaturemask=0xfff7bffb` failed identically, so clock
gating and PCIe DPM are excluded.

- During the hang, GRBM_STATUS a0403028 / SE0 08000006: only SPI and CP are busy;
  VGT, PA, SC, CB and DB are idle.
- wavedump finds 64 live waves, about 6-7 per CU on all 10 CUs. EXEC is all ones and
  STATUS has VALID set and EXPORT_RDY clear. Every wave is at PC 0x0060004c with
  INST c40008cf 06050402 (`exp pos0 ... done`), identical in both samples.
- Their SGPRs are the compute dispatch's user data: s4 = 0x00100440, s8-s12 = the image
  descriptor. The dispatch is 64 groups x 64 threads. So these are compute waves
  executing vertex-shader code at offset 0x4c.
- The registers keep their last values after recovery: COMPUTE_PGM_LO 0x4002, VS 0x4000,
  PS 0x4001. The shader BO is 2 MB at 0x400000, so the waves ran off its end into the
  next buffer.
- The BAR resize fails (`Problem resizing BAR0 (-22)`), so not all VRAM is CPU-visible.
  radeonsi then uploads shaders through a staging buffer and CP DMA on its compute-only
  `shader_upload` aux context. Compute rings comp_1.0.1/1.0.2 advanced (5 and 2) while
  gfx advanced by one.
- `polaris11_le_user_ib` gave only GFX user IBs `is_le`. Compute IBs were fetched with
  swap 2, so the LE copy packets were read byte-reversed, the code never reached VRAM,
  and the zero-filled BO executed as no-ops up to the next buffer.
- drm-shim reports all VRAM visible and never takes this path, which is why an offline
  x86 versus PPC IB comparison matched.

## Kernel016 and result (hardware-016-001), 2026-11-14

Build: kernel015 tree + `0035-amdgpu_cs-hunk.patch` (sha256 ed2ddd9e...). The config
differs from 015 only in LOCALVERSION (`-tabor-e2e-016`), config 71738b3c...,
amdgpu.ko 76349abe59607a19b35276adc83ac73e346d29b4a3025bbd04738ec78ab8008a, Module.symvers
7ce6a440... (unchanged). Scripts: `scripts/make-0035.sh`, `scripts/build-016.sh`.

Fresh power-cycle boot, module hash verified in place, root RO, taint 0 before load. One
`modprobe amdgpu polaris11_le_user_ib=1`, default `cg_mask`/`ppfeaturemask`. Results:

| test | result |
|---|---|
| gfx-write le / le vram / le uswc | PASS |
| gltest clear (radeonsi, ACO) | PASS, 0/4096 bad, ff8040ff, 3 s |
| gltest draw (VBO, compiled VS/PS) | PASS, 0/4096 bad, 00ff00ff |

No live waves remain afterwards. gfx fence 7 -> 8 -> 9, no timeout, recovery or fault in
the kernel log. Taint 0 at the end. The only amdgpu error line is the known BAR0
resize -22.

## Limits

Offscreen only: no KMS/GBM display path, no desktop. Two small probes, not a conformance
run. Userspace VCE IBs are still unconverted. The root filesystem of this stick carries
an ext4 error from an earlier forced read-only remount; it does not affect the GPU
results. Build environment as in vce-le-20261113 (contributor workstation, trixie
container, GCC 14.2.0 / binutils 2.44).
