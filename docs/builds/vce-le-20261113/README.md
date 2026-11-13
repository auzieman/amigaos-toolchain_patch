# Kernel015: VCE software little-endian messages (patch 0034)

Second A1222 (Polaris11 1002:67ff rev 0xff, subsystem 1002:0b04, 10 CUs) running the
forge rescue stick: static BusyBox/Dropbear root, kernels on one USB stick.

## Kernel014 reproduced (hardware-014-001)

Rebuilt from 007 + 0028-0033 + kernel014's trace patch. Every boundary input/output
hash, the 15-file chain, config 9d0bc944... and amdgpu.ko 099a4e24... match
build-014-receipt.json (byte-identical module; Module.symvers 7ce6a440...).
One modprobe, root RO: rc 0, taint 0, fbcon on HDMI. debugfs amdgpu_fence_info
gives direct evidence that 0031 cleared the gfx IB test: gfx 1/1 signaled/emitted.
Only failure: `IB test failed on vce0 (-110)`, vce0 0/2 (fences emitted, never written).

## Cause

vce_v3_0_mc_resume writes VCE_LMI_SWAP_CNTL/1 = 0 unconditionally (no __BIG_ENDIAN
arm, unlike uvd_v6_0.c:776), while VCE ring words and the kernel-built create/destroy
messages (amdgpu_vce.c) were stored CPU-native. VCE ring test only checks rptr
movement, so it passed with garbage commands.

## Patch 0034 (sha256 48c83f99015029a0346685e57e13098983d8fb65d9c5928dc1691d241d75302b)

- amdgpu_ring_uses_sw_le(): add AMDGPU_RING_TYPE_VCE (Polaris11 BE only).
- amdgpu_vce_encode_ib(): store kernel VCE create/destroy message words cpu_to_le32
  before submission. Hardware swap stays 0 (same strategy as gfx/compute/UVD_ENC
  and the AmigaOS amdgpu-gcn driver).
- Not covered: userspace VCE IBs (amdgpu_vce_ring_parse_cs reads them natively).

Build: 014 tree + 0034, config identical to 014 except LOCALVERSION (-tabor-e2e-015),
config f0c248f8..., amdgpu.ko 8b6cb5825e9e644cdbc501d704bfe9762bdf622550951f0a375719e7acf962f0,
Module.symvers unchanged. Scripts in scripts/ (run in the forge trixie kernel container).

## Physical015 (hardware-015-001), 2026-11-13

Fresh power-cycle boot, release/module hash verified, root RO, taint 0 before load.
One `modprobe amdgpu`: rc 0 in 13.2 s, taint 0, SSH survived, fbcon amdgpudrmfb on
HDMI-A-1. **No IB test failure.** Only error line: the known BAR0 resize -22.
Fences (signaled/emitted): gfx 1/1, comp_1.0.0-7 1/1, sdma0 0x15/0x15, sdma1 1/1,
uvd 2/2, uvd_enc0/1 2/2, **vce0 2/2** (vce1/vce2 are not IB-tested by amdgpu).
All kernel amdgpu self-tests pass on this board. GL/userspace not tested here.

## Build environment and limits

Built on a separate contributor workstation, not the R730: Docker debian:trixie with
gcc-14-powerpc-linux-gnu 14.2.0-19cross1 / binutils 2.44 (same pins as 007), all host
CPUs, no explicit CPU/memory limit. 014 reproduction is byte-identical to the R730
module despite that. Rescue root is the forge-side static BusyBox 1.37.0 / Dropbear
2025.88 userland, not the R730 RAM helper. No GL/Mesa, VCE encode or userspace VCE
tested; only the kernel's own IB self-tests.
