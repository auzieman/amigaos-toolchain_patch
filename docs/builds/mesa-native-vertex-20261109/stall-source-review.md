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

## Structural-layout follow-up: numeric shader state

Decoded the retained400DW canonical point IBs using packet boundaries, then
SET_SH_REG/SET_SH_REG_INDEX offsets. Both x86 and SPE produce identical values:
VS PGM_LO=0x6000, PGM_HI=0, RSRC1=0x2c0040, RSRC2=0x12;
PS PGM_LO=0x6001, PGM_HI=0, RSRC1=0x2c0043, RSRC2=0xe.
Program addresses reconstructed in256-byte units are VS0x600000/PS0x600100.
These are offline shim addresses, not physical failing-run addresses. This
checks the numeric packed state, beyond endian serialization, for that capture.
It does not establish residency, executable destination contents or validity of
all required state. No divergence in these eight shared shader fields found.

Inspected ac_hw_cache_flags producer and union: packed gfx12 bitfields are
outside Polaris/GFX8; applicable GFX6-8 producer uses numeric value bits instead.
Do not transplant the float_mode fix into an inactive gfx12 union as a claimed
Polaris correction. Operand/Definition control unions initialize zero and named
flags remain compiler-local; no analogous exported packed numeric alias was
identified in the inspected declarations. No new root-cause fix claimed.

## Extracted upload-loop bounds execution

check-upload-bounds.py extracts actual get_shader_binaries/upload_binary_raw
from the final Mesa source and runs on R730 with guarded mocked allocation,
pre/post hooks, symbol resolver and UBSan. All8 prolog/previous/epilog combinations
pass with conversion branch disabled and enabled (16 cases). Constant tails and
allocation guards match. Native-host bswap branch is not PPC ABI execution.

Negative controls: exec_size32/code_size4 causes SIGSEGV via unchecked size
underflow/copy; a deliberately out-of-range mocked symbol write trips the tail
guard (SIGABRT). These demonstrate a real missing metadata defense in the
inspected loader, not that valid compiler output in our failed trial violates it.
Actual ACO relocation semantics are not tested by the mocked resolver. No new
GPU driver patch or hardware test; source hash and results retained. Initial
harness attempts hit a non-writable work directory and missing stdbool include;
corrected to owner-private work path and explicit header before accepted runs.

## Direct/bulk ring writer bypass audit

Searched kernel013 gfx_v8_0.c, amdgpu_ring.c/.h and amdgpu_ib.c for direct
ring indexing and bulk writes, then checked repository-wide hits for active
GFX8 callers. Ring clear, scalar writes and conditional-execution backpatches
all call encode_dw. write_multiple routes the targeted software-LE ring through
scalar encoding and returns before the memcpy fallback. GFX8 CE/DE metadata
bulk callers build native fields; they are behind the SR-IOV/preemption branch
in the IB emitter, not the ordinary bare-metal path. Diagnostic ring-pointer
reads do not modify data. No active GFX8 bypass found in these writers.

Ring-mux copying existing ring storage through write_multiple would require
careful representation ownership if enabled with software-LE rings; its init
callers are GFX9, not this Polaris/GFX8 path. Do not claim it caused this hang.
JPEG/newer-GFX direct stores found by global search likewise are not this ring.
GFX8 read/write pointer helpers decode/encode when software-LE applies; zero
initialization is endian invariant. This review found no new faulty expression
and does not establish whole-driver conversion completeness.

The sample GPU address0x0000000312345678, packet header0xc0023200 and explicit
low/high slots produce bytes003202c07856341203000000 after per-word conversion,
identical to x86. This demonstrates that explicit slot order is preserved;
word-sequence reversal would corrupt this packet rather than fix it.

## AMD reference comparison and envelope trace candidate

AMD PAL commit2de164b431f8a27652e63513ae73338dc512e5bf packet headers and
builders were fetched and SHA256-verified against prior packet-source.json.
BuildIndirectBuffer explicitly emits low/high address fields, VI validity and
preemption bits. Kernel GFX and compute envelopes are different: do not infer
missing VI VALID in the longstanding kernel GFX emitter is a PPC fault solely
from PAL userspace construction. BuildWaitRegMem defines memory/register space,
comparison, engine, reference and mask. BuildEventWriteEop documents alignment,
48-bit address limit and confirmation selectors; kernel emits dummy+real events
with different interrupt choices. These require decoded semantic comparison,
not word-sequence reversal or blind PAL struct copying on BE.

Prepared0013-opt-in-prepublish-envelope-trace.patch for exact kernel013 source.
Defaultoff module parameter polaris11_submit_trace, writable root-only; arm
later after init if built/qualified. Captures first16 targeted GFX envelopes,
up to512 raw dwords each, IB addresses/lengths/flags/LE contract, VMID and fence
sequence/address/raw decoded completion. Reads only existing CPU mappings,
never submits work or accesses MMIO. Runs after late packet backpatches and
before ring commit/doorbell. Final alignment NOPs added inside commit are not
captured. Logging changes timing and can perturb behavior. Bounded output is
still substantial and requires offboard collection. IB list logs capped16.

Patch dry-run against exact pinned source passes. No kernel source modified,
compilation, deployment or hardware trial in this pass. This is diagnostic code,
not a root-cause fix. Its purpose is to capture the kernel waits/setup/completion
that the prior Mesa-only snapshots omitted, and associate5/6 with actual packet
positions and addresses before automatic reset destroys original state.

## Executed GFX8 constructor contract checks

check-gfx8-contract.py extracts exact kernel013 IB-GFX, EOP-fence-GFX and
pipeline-sync emitters, with actual vid.h packet macros. Runs on R730 using
native GCC and accepted SPE SDK8.5 plus QEMU e500v2. Both pass2816 cases:
512 IB cases (four addresses including >32bit/48bit, four lengths through20bit
maximum,16VMIDs,CE/nonCE);2048 EOP cases (32/64bit write, interrupt/EXEC flags,
dummy/real values including carry across32bits);256 pipeline-wait cases.
Numeric ordinal fields and explicitly serialized LE bytes are checked against
independent PAL field-position definitions. EXEC bit28 is from kernel vid.h,
not specified by the older PAL EOP struct. Some kernel choices (GFX IB VALID
and interrupt selectors) differ from PAL user-mode builders; test establishes
field packing, not that every selected policy is appropriate for hardware.

The ring writer and structs are mocked; explicit byte checking does not execute
actual kernel publication/accessors. Non-SRIOV only, opt-in is_le=true. This is
actual PPC32 compiler execution, not a simulatedBE branch on x86. It establishes
no numeric/byte divergence for these constructor inputs, not runtime-state,
VM mappings, descriptor contents, firmware, visibility or GPU execution.
Harness setup initially used sid.h instead of gfx8 vid.h and omitted event enum;
corrected before accepted runs. No physical workload/build/deployment change.
