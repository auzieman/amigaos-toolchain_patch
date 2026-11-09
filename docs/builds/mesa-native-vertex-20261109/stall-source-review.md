# GFX completion and recovery source review — 2026-11-09

Read-only review of deployed kernel013 source on R730. No new hardware workload,
reset, reload, boot change or source patch. Manual post-stall snapshot is retained
in physical-rgb-001/manual-poststall.txt.

## Original timeout

amdgpu_job_timedout reports fence_drv.last_seq (atomic CPU bookkeeping) and
fence_drv.sync_seq (latest emitted sequence). These are not a program counter or
a command-buffer identifier. The 5/6 report does not identify the failing draw,
shader, instruction, or exact submission contents.

amdgpu_fence_read already uses le32_to_cpu on the mapped kernel completion word;
amdgpu_fence_write uses cpu_to_le32. This is distinct from the Mesa LE64 user
fence fix. Do not apply that fix again to native dma_fence structures.

amdgpu_fence_process reads the mapped word and signals pending dma_fences.
A fallback timer also calls fence processing: an absent interrupt alone is not
sufficient to explain a persistently unobserved completion if the mapped value
is visible and the timer path runs. Those conditions are not measured here.

gfx_v8_0_ring_emit_fence_gfx emits a dummy EVENT_WRITE_EOP with sequence-1,
then the real EVENT_WRITE_EOP with the requested sequence and optional interrupt.
Both request cache flush/writeback. Thus a value of5 could be an earlier completed
fence or the dummy write associated with6; the log alone cannot distinguish.
Missing6 can result from stalled preceding work, an EOP/cache-drain stall,
incorrect packet/address publication, or a completion visibility problem.
The source review does not select a proven cause among them.

## Secondary recovery stall

Observed stack: amdgpu_device_gpu_recover -> amdgpu_do_asic_reset ->
amdgpu_device_ip_resume_phase3 -> amdgpu_display_resume_helper ->
drm_helper_resume_force_mode -> drm_crtc_helper_set_mode ->
amdgpu_dpm_compute_clocks -> amdgpu_fence_wait_empty -> dma_fence_wait.

amdgpu_dpm_compute_clocks drains every ring whose sched.ready is true before
calling pm_compute_clocks. amdgpu_fence_wait_empty waits uninterruptibly with no
finite timeout for the latest retained fence. A reset-time ready ring with a
pending unsignaled fence can therefore block display restoration. The stack
establishes the wait, but not which ring or whether this is an old or replayed
fence. Buffer deletion and process VM teardown also wait on fences downstream.
A successful ASIC-reset message does not establish completed recovery.

## Next discriminating evidence

Before another physical workload, review the complete kernel ring producer and
Mesa IB publication together. A future cold-boot capture should correlate ring,
fence GPU address, sync/last sequence, raw and LE-decoded mapped completion word,
and command progress before reset destroys the original state. Preserve the
original timeout independently from recovery. Do not bypass fence waits or force
success as a render fix. Full physical RGB IB stderr was not retained in the last
trial, so do not claim to reconstruct its exact command stream from offline runs.

## Connected publication follow-up

Inspected exact kernel013 and final native-vertex Mesa sources, read-only:

| Boundary | Observed implementation | Review result |
| --- | --- | --- |
| Mesa IB finalization | amdgpu_ib_finalize before shared serialization; previous/current chunks serialized before submission-context swap | No late size fixup found inside reviewed finalization path |
| Mesa chain pointer | address split low/high, size patched before final serialization | No extra hardware endian-swap bit in chain address |
| Kernel user IB intake | native ioctl fields -> gpu_addr, length_dw; Polaris11/GFX option sets is_le | Matches intended paired Mesa flag; ioctl metadata is not swapped |
| Kernel IB packet | gfx_v8_0_ring_emit_ib_gfx selects swap0 for is_le, swap2 for native legacy IB | Preserves different kernel/user IB contracts |
| Ring packet words | amdgpu_ring_write and write_multiple -> encode_dw | Shared software LE for Polaris11 GFX |
| Late conditional count | amdgpu_ring_patch_cond_exec -> encode_dw after native distance calculation | Late backpatch is covered, zero comparison endian invariant |
| Ring fetch setup | cp_gfx_resume disables BUF_SWAP for software LE ring | Consistent with serialized ring, distinct from IB fetch swap |
| Publication | amdgpu_ring_commit pads then mb then set_wptr | Explicit barrier exists; this does not prove platform DMA visibility |
| Pointer publication | memory WPTR encoded; doorbell/MMIO receives native numeric value through accessor; MMIO path readback | No justified extra word swap at caller |
| Completion | GFX EOP emitted through same ring writer; mapped fence LE32 decode | No missing conversion identified in these reviewed calls |

The schedule also emits VM/pipeline synchronization and HDP flush before IB
execution. Those wait packets can stall before a shader runs. They cannot be
excluded by matching Mesa executable bytes or a VMID0 CP_WRITE_DATA control.
Next review must close VM page-table publication/TLB invalidation, HDP wait and
pipeline-sync dependencies, plus shader BO upload/visibility. No root cause or
patch is claimed from the consistency findings above. No fresh GPU trial run.

## Murphy review: VM and synchronization

The exact non-x86 amdgpu_vm_manager_init forces vm_update_mode=0, regardless
of the module parameter; the regular VM update path is SDMA. A proposed
vm_update_mode CPU-control boot would not exercise the intended alternate path
without a reviewed kernel change. No such change or boot was made.

SDMA command ring and IB words remain CPU-native and sdma_v3_0 enables hardware
RB_SWAP_ENABLE/IB_SWAP_ENABLE on BE. amdgpu_ring_uses_sw_le excludes SDMA.
This is consistent with sdma_v3_0_vm_write_pte/set_pte_pde writing native packet
fields. Raw GART-derived PTE arrays stored at the IB tail instead use
cpu_to_le64, and copy_pte uses a byte copy with src/dst endian swap0. These are
two different contracts; serializing the entire allocation would break raw
payload or commands. The PTE copy source uses num_dw_left*4; destination advance
uses count*8, consistent with DW and 64-bit-entry units respectively.

The alternate CPU setter uses writeq, whose PPC accessor is little-endian;
absence of an explicit cpu_to_le64 at its call site is not a missing conversion.
CPU commit includes mb and HDP flush. This is source consistency, not active-path
hardware acceptance.

amdgpu_vm_flush emits pipeline sync when requested, page-table base pd_addr>>12,
TLB invalidate and PFP/ME synchronization, then can emit its own kernel fence
before the user IB. Therefore signaled5/emitted6 must not be interpreted as six
Mesa submissions or as proof that the sixth draw was reached: a kernel VM-flush
fence can contribute to the same sequence counter. Its identity in this trial
is unrecorded.

Pipeline WAIT_REG_MEM compares the prior native sequence numerically against
GPU memory; packet fields pass through the ring encoder. HDP flush waits for
specific engine bits in GPU_HDP_FLUSH_DONE. A wrong reference, stale writeback,
wrong engine selection or failed VM update can block before shader execution.
No contradiction found in inspected packing; actual wait progress is not captured.

Shader upload captures precede the staging-to-VRAM CP DMA copy. post_upload_binary
adds buffer barriers plus ICACHE/L2 invalidation and flushes its auxiliary context.
Thus matching captured shader bytes proves the CPU source, not final executable
VRAM contents or cross-context dependency completion. Earlier direct-upload
negative control limits a staging-copy-only explanation but does not close VM
mapping or instruction-fetch visibility.

Breakage cases still requiring discriminating evidence: final physical PTE
contents versus intended addresses/permissions, VM update dependency completion,
HDP/pipeline wait progress, actual shader destination contents and addresses.
No speculative extra swaps or weakened waits introduced in this review.

## Packet-body and address injection audit

Read the actual pre_upload_binary -> upload_binary_raw ->
si_aco_resolve_symbols -> post_upload_binary chain. The normal shader BO requests
SI_RESOURCE_FLAG_32BIT and 256-byte alignment. VS/PS program registers pack VA>>8
and address32_hi>>8. The winsys translates the resource flag to
AMDGPU_VA_RANGE_32_BIT. A wrong allocation high segment or mapped backing would
still redirect instruction fetch; matching executable files cannot exclude it.

Symbol replacement writes native numeric instruction fields before executable
serialization. Shader constant-data tail is memcpy'd separately, not blindly
swapped. Earlier standard-test captures match executable bytes, but this does
not qualify all future constant-data producers or relocated scratch shaders.
No late post-serialization symbol write found in this function chain.

si_emit_cp_dma packs low/high source and destination addresses numerically,
byte count and synchronization bits into the same GFX IB serializer. The copy
moves already-serialized shader bytes; swapping the copied body again would
corrupt instructions. si_cp_dma_prepare adds source/read and destination/write
BO references, a first-copy barrier/RAW_WAIT and last-copy SYNC.

amdgpu_set_ib_size writes native size/control fields; finalization precedes
serialization. Chain pointers are low/high native integers and join the final
serialization. This inspection found no native late backpatch after serialization
in that chain. The user-queue packet builder is a separate entrypoint; it must
not be treated as evidence about this legacy Polaris ioctl submission path.

Ordinary descriptor and constant upload use util_memcpy_cpu_to_le32 upstream.
The shader-cache memcpy routines in si_state_shaders are CPU serialization/cache
storage, not direct GPU publication; they are not evidence of missing GPU swaps.

The evidence gap is now stated at concrete objects: actual shader BO VA and
contents after copy, PTE mapping backing that VA, prerequisite fence/wait progress,
and raw completion memory before reset. No code defect is established by this
pass; no runtime source change, build or physical workload was performed.

## Own-patch bounds review

Inspected amdgpu_ib/amdgpu_cs declarations before judging the cast in
amdgpu_set_ib_size: main_ib is explicitly the first member of amdgpu_cs, and
reviewed finalize/check-space callers use that member. This is intentional
embedding, not evidence of an invalid unrelated-struct cast at these callers.

Inspected full opencoded_load_format storage rather than its diff alone:
loads[32], native load count at most8 (four doubles), pair swapping requires an
even count and uses i+1 within it; native 8/16/32-bit channels use at most4 slots.
Native scalar helper shifts range0..bits-8 for supported8/16/32/64 widths;
8-bit values return before the loop. No overflow of that local array or
out-of-range shift found. This does not qualify external buffer descriptor
bounds or arbitrary invalid format metadata. Existing real-NIR tests remain
separate evidence; no new modeled test is offered as hardware proof.

The upload fix writes exec_size/4 words inside each copied executable part;
constant tails are copied at cumulative exec_size, and allocation uses cumulative
code_size. Correctness depends on exec_size<=code_size, checked arithmetic and
symbol offsets inside executable storage. Existing inspection of loop shape
alone is not a complete bounds proof for compiler-provided metadata. These
producer invariants are the next concrete source-level audit targets.
