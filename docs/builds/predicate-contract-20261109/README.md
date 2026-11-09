# Conditional predicate encoding contract

Physical010: user confirms readable local console; SSH remains alive, taint0. GFX IB selftest still times out. CPU-visible rptr and wptr both decode as0x600, matching submitted end1536. Envelope starts1280. COND_EXEC at relativeword5 skips28dwords to relativeword38, covering the HDP handshake, IB descriptor, HDP invalidate and both fence packets. The snapshot captures128 of256 submitted words; the final padding is not fully captured.

Captured predicate bytes are00 00 00 01: native BE one, GPU LE0x01000000. The runtime setter already calls the scoped amdgpu_ring_encode_dw helper, but amdgpu_ring_init writes native1 directly. This is a gap in our conversion coverage: the earlier shared-setter change did not include initial setup. Patch0031 changes that initializer to call the existing runtime setter. No command, timeout, conditional block or fence is bypassed.

Cross-architecture executable fixture extracts the actual encoder/runtime setter and old/new initializer expressions. x86 bytes remain01 00 00 00. Selected PPC initializer changes from00 00 00 01 to01 00 00 00, matching the existing setter. Unselected rings retain native behavior. Selection is modeled; this proves a byte-contract inconsistency, not GPU causality. Both integer interpretations are nonzero, so a GPU nonzero comparison could still accept the old representation. Exact predicate evaluation and memory visibility remain hardware questions.

All occurrences of cond_exe_cpu_addr and calls to the runtime setter in the pinned AMDGPU source were reviewed. Initialization is the remaining direct nonzero store; other writers use the shared setter. The one-line change fixes the owning initialization boundary, rather than rewriting per-engine features.

Parent:6.12.113-tabor-e2e-010. New matched candidate011 is prepared on R730 with the010 CPU-only diagnostics retained. No live driver reload or GPU register probing is performed.

011 full build:43modules and687 imported symbol CRCs verified. Versioned kernel/DTB/modules and boot-011.scr are installed inactive; copied-file hashes and script readback match.010 remains selected and root is read-only. No reboot or driver reload has occurred.
