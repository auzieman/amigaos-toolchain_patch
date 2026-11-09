# Native DRM acceptance on physical candidate011

Read-only AMDGPU_INFO probe: accel_working1, GFX available mask1, compute15, SDMA3, UVD1, UVD_ENC1. VCE reports mask1 despite VCE0 selftest failure: available_rings is produced from the count of ready rings and is not proof the failed encoder works. No CS, modeset, reset or GPU command submitted by this probe. Kernel query implementations were inspected first.

The first probe segfaulted in userspace because its handwritten syscall wrapper omitted volatile-register clobbers. The wrapper was corrected. A missing-device control binary passed under qemu-ppc/e500v2 before the corrected board query. This was a probe defect, not a GPU/kernel failure.

Then unmodified Debian libdrm-tests2.4.124-2/modetest, libdrm2 and libc6 2.41-12+deb13u4 from the accepted libdrm build's inputs were SHA-verified against its receipt, extracted into an isolated temporary test bundle, and executed on the board. No package install state was changed; this is not a completed Debian rootfs installation. Required loader/libc/libm/libdrm and modetest occupy a3,532,800-byte tar; installed only in /run/debian-drm.

QEMU help-path check passed. Physical command:

```
/run/debian-drm/usr/lib/powerpc-linux-gnuspe/ld.so.1 --library-path /run/debian-drm/usr/lib/powerpc-linux-gnuspe /run/debian-drm/usr/bin/modetest -M amdgpu -c -p
```

Exit0, AMDGPU3.61 opened; connected HDMI-A-1 connector54, preferred1920x1080/60Hz,17 modes. Complete connector/CRTC/plane output retained. No modeset, pageflip, GL context, shader or video encode was requested. This establishes native packaged userspace/DRM compatibility, not accelerated rendering acceptance.

Remaining VCE source gap: create/destroy messages in amdgpu_vce.c write native IB words, and VCE3.0 sets LMI_SWAP_CNTL/LMI_SWAP_CNTL1 to0. The selected primary-ring LE helper currently excludes VCE. Before changing it, both primary-ring and firmware-message contracts need paired review; a zero-valued END primary-ring test is not sufficient to validate nonzero VCE opcodes. No VCE patch or live retry was performed.
