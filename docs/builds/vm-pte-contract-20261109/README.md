# GPU VM PTE serialization — 2026-11-09

Candidate012 fixes a demonstrated byte-contract defect in the exact011 source.
Physical causality and rendering acceptance remain pending a new boot.

The independent userspace GFX WRITE_DATA tests complete their fences but leave
an allocated GTT target at zero, both with native BE and explicit LE command
words. A separate native test below4GiB behaves the same. Thus neither ACO nor
EGL is required to reproduce missing data; these tests do not alone prove a
particular GPUVM or CPU-coherency cause. They write only their allocated buffer,
never registers or display state. SSH survives and taint remains0.
See ../radeonsi-aco-20261109/gfx-write*-result.txt and source/launch helpers.

Source trace for system-memory mappings:

1. amdgpu_vm_map_gart returns a native physical-address integer.
2. amdgpu_vm_sdma_update combines the address/flags into a native uint64 array
   placed at the unused end of its IB allocation.
3. amdgpu_vm_sdma_copy_ptes passes that array's GPU address to vm_copy_pte.
4. sdma_v3_0_vm_copy_pte emits COPY_LINEAR with src/dst endian-swap control0.
5. Consequently native BE page-entry bytes are copied unchanged into GPU page
   tables. SDMA command-fetch byte swapping does not transform a raw DMA source.

Patch0032 gives the array the __le64 type and serializes the complete native
address|flags exactly once at its producer. SDMA command words, page-address
inputs, contiguous VRAM PTE generators and MMIO accessors stay unchanged.
This shared producer affects GTT mappings used throughout the GPU workload.
No unrelated per-feature shader edits are included in this kernel candidate.

check.py extracts the actual old/new assignment block; mapped addresses and
flags are supplied/modelled, and DMA copying is modelled as byte-preserving.
256cases per architecture pass with a real old-BE negative control. Fixed BE
and unchanged x86 match the independently packed LE expected array. This is a
serialization test, not a GPU simulator or physical acceptance.

Parent complete kernel011 is cloned privately using reflinks on R730. Build012
uses the retained pinned kernel6.12.113/GCC14 build image, two compile jobs,
existing container resource bounds, matching modules/DTB/firmware/CRCs and the
normal bundle checks. No USB writes, live driver reloads, or saved boot-script
changes are part of the build. Candidate receipt records final outcome.

Separate userspace repair: kmscube lacked the legacy ADDFB fallback required
by drm_mode_addfb2_ioctl's deliberate BE compatibility gate. The restricted
XR24/AR24 fallback now physically registers framebuffer59 successfully and
reaches modesetting, but the draw still reads black. Native float API bits
are correct (red/alpha3f800000), complete framebuffer, no GL error; disabling
DCC does not restore the red-clear result. Old staged libdrm_amdgpu was also
replaced with the hash-verified matching Debian package library; black result
persists, so that assembly inconsistency is corrected without claiming cause.

Next acceptance: complete candidate012 receipt, stage its complete bundle with
011 rollback preserved, boot012, repeat the independent native GFX write first,
then solid-red clear and a bounded cube/readback only if those gates pass.

## Build and deployment checkpoint

012 complete bundle accepted:43modules,687matching AMDGPU symbol CRCs; module
SHAd26c85e311ce5c13e4625f7dc3f8bc898a04b6dc91dcc4d1d7816630344dbfbc.
Cruzer serial03007431041721021451/rootPARTUUIDa1221108-02 verified before
installation. All staged kernel/module/DTB bytes and U-Boot script read back
correctly. /boot.scr selects012; boot-011-rollback.scr retains exact011 script.
FAT unmounted and root restoredRO. Running board remains011; no reboot issued.
Physical012 PTE/GFX/GL validation is pending. Existing startup command is reused.
