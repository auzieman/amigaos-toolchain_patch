# UVD encoder shared-codec candidate

The e2e-002 physical trial passed the UVD decoder ring but timed out in uvd_enc0. This candidate extends the existing Polaris11 shared software-LE ring policy to AMDGPU_RING_TYPE_UVD_ENC. It changes no packet constants, decoder ring, register accessor, other ASIC policy or generic PCI/DMA implementation.

Encoder END is1. The old BE producer stores bytes00 00 00 01; a little-endian firmware consumer reads01000000. Candidate shared serialization instead stores01 00 00 00, matching x86. This remains conditional on the actual encoder fetch contract; we did not capture the physical encoder buffer in e2e-002.

## Source review

Both encoder instances use UVD_RB_* base/size/pointer registers. The decoder uses distinct UVD_RBC_RB_* registers. UVD_LMI_SWAP_CNTL has decoder RB/IB swap fields; no explicit encoder-specific swap setup was found in this initialization sequence or named swap fields for the encoder ring in the reviewed UVD6 header. This is not hardware proof that encoder firmware performs no swap. The candidate does not change that register because the decoder now passes with its existing policy.

Both encoder read pointers use RREG32 and write pointers use WREG32. Those register boundaries already receive Linux PPC accessor conversion. The candidate leaves them intact; adding another software swap would corrupt values there.

All tested encoder packet emitters use amdgpu_ring_write, so changing its existing policy covers END, IB_VM, FENCE, TRAP and NOP without rewriting each command. Referenced IB payloads are separate objects and are not made correct merely by encoding the containing ring packet.

## Standalone results

The test extracts14 actual driver functions:7 ring helpers, the encoder test, END/IB/fence emitters, generic NOP insertion and encoder register read/write accessors. Ring allocation/commit and registers are simulated. It executes128 cases (2encoder instances x64start offsets) for each old/candidate and x86/PPC combination:512 cases. Additional14-dword wrapped IB/fence/END/NOP expectations check VMID, high/low GPU addresses and sequence values. Predicate tests preserve decoder, SDMA and other ASIC behavior.

Old PPC reproduces timeout in the assumed no-hardware-swap model. Candidate PPC matches unchanged x86 output exactly, including modeled pointer responses. Existing standalone missing/double-conversion controls rerun successfully. No module or real GPU was accessed. Initial fixture compilation required adding missing bool literals and a freestanding memset; these were test scaffolding fixes, not kernel changes.

The test assumes LE firmware fetches with no hardware swap; it validates representation and routing, not actual firmware interpretation, DMA coherency or hardware timing. Real IB execution, fences, encoder workload and framebuffer acceptance remain open.

Full fresh e2e-003 kernel/modules/DTB build is launched on R730, pinned image and parent identities,4CPUs/6GiB, no network. Build status and artifact identities must be checked before deployment. A1222 remains on the prior failed trial; no reboot or deployment performed in this round.

Full e2e-003 build completed successfully:43modules, AMDGPU687versioned imports verified, U-Boot CRC/load checks and bundle hashes pass. Module SHA48799ed982a9e52f189d22e8f9d142fcc1db048ecacc35fba6c69eb7a8b42f16. Not installed or hardware tested; previous A1222 boot files untouched. See build-receipt.json.

2026-11-08 fresh e2e-002 boot reached SSH, taint0/no AMDGPU. Installed complete e2e-003 candidate over SSH after USB serial and old boot hash checks; all staged/installed payloads verified, firmware aliases preserved. /boot.scr now selects /boot/e2e-003; exact e2e-002 selection retained as /boot-e2e002-rollback.scr. FAT synced/unmounted. Running kernel remains e2e-002, no GPU load, no reboot. Candidate physical boot/encoder acceptance pending. See live-deploy.json.
