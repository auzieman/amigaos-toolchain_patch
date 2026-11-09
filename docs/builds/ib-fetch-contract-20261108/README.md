# GFX8 indirect-buffer fetch investigation

Candidate009 physically boots; the user confirms readable HDMI console and continued responsiveness. Its single first-bind trial still returns GFX IB -110. Payload remains cafedead, fence remains zero, sequence one remains unsignaled. This does not distinguish missing GPU execution from CPU visibility problems.

## Complete selftest submission path, audited against candidate009

1. `gfx_v8_0_ring_test_ib`: allocate WB payload and direct-pool IB; initialize payload LE. Candidate009 serializes all five IB words LE and requests no hardware fetch swap. Native AVFS/user IB contracts remain separate.
2. `amdgpu_ib_schedule`: reserve primary ring. The allocator sets AMDGPU_IB_FLAG_EMIT_MEM_SYNC even though the caller initially zeroes the object. Consequently SURFACE_SYNC executes before COND_EXEC/HDP/IB. With NULL job, job VM flush, context-control, explicit pipeline sync and user fence paths are absent. The earlier zero-flags inference was incorrect; allocator side effects are part of the actual flow.
3. GFX8 `COND_EXEC`: GPU reads conditional predicate in WB memory. Native CPU initialization is one, whose LE interpretation is 0x01000000 on BE; both are nonzero. This difference alone does not establish a skipped envelope.
4. `amdgpu_device_flush_hdp`: ring-specific flush/wait precedes IB execution. GPU-side WAIT_REG_MEM request/done handshake is an unobserved boundary. Its words go through the existing primary-ring encoder.
5. GFX8 IB descriptor: address low/high, length and VMID; VMID0 selftest. Candidate009 pairs explicit LE bytes with swap0; candidate008 paired native BE bytes with swap2. Both physical trials time out.
6. HDP invalidate and two GFX EOP events, then conditional-count backpatch. `amdgpu_ring_patch_cond_exec` already encodes the backpatch with `amdgpu_ring_encode_dw`.
7. Commit: NOP padding, `mb()`, write-pointer publication. Selected GFX8 WB producer pointer is explicitly encoded; doorbell/MMIO values remain native accessor arguments.
8. GPU WB payload/fence and CPU fence reader: sentinel and fence are LE; fence reader already uses le32_to_cpu. Interrupt/wakeup is downstream of GPU fence publication.

The passing primary-ring test writes SCRATCH_REG0, not the IB-test payload or EOP fence. It proves a short ring fetch/register operation, not the entire conditional/HDP/IB/memory-write envelope. Ring and IB allocations share the BO/GART family; that weakens a blanket broken-GART explanation but does not establish each mapping/address/publication contract.

## Next discriminating capture

Patch0030 snapshots the complete CPU-mapped submitted primary-ring envelope (up to128dwords), all five IB words, CPU-mapped read/write-pointer bytes, conditional predicate bytes and addresses after the existing timeout. It adds no GPU command, MMIO access, reset, recovery or live rebind. This provides the actual byte stream including the preamble and backpatch instead of testing only the IB emitter in isolation. CPU snapshots still cannot prove a GPU read or establish coherence.

Candidate009 remains running unchanged. No second driver load is authorized by this investigation workflow after its failed selftest. A future candidate requires a matched build and fresh boot.

## Offline-test limits

The 512-case per-policy/per-architecture source fixture passes. It models scheduler/GPU endpoints and therefore did not validate the actual scheduler envelope or hardware HDP handshake. Physical009 is a negative result for the isolated IB-fetch swap hypothesis, not a validation of that model as a GPU simulator.

## Candidate010 ready, inactive

Full matched build passed:43modules and687 imported AMDGPU symbol CRCs. The versioned010 kernel/DTB/modules and boot-010.scr are copied to the live USB and readback hashes verified.009 remains selected in boot.scr, with008 rollback retained. Root returned read-only; no driver reload or reboot occurred. Decoder opcode names were checked against pinned vid.h; framing tests reject truncation and byte-swapped control streams. The010 patch changes diagnostics only and does not claim to repair acceleration.
