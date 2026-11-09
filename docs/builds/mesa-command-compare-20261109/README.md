# Finalized GFX command-stream cross-architecture comparison

2026-11-09. Source review and offline execution only; no board calls, deployment,
render attempt, reset or reboot in this pass.

## Result

The unchanged upstream Piglit constant-point test produces one finalized
400-dword GFX indirect buffer on both native x86 and QEMU e500v2 SPE with the
same upstream no-op Polaris12 profile. After encoding CPU-constructed numeric
words canonically as LE, 399 words are identical. The sole difference is
CB_COLOR0_INFO.ENDIAN: x86 NONE (0), SPE 8IN32 (2).

The comparison decodes its SET_CONTEXT_REG packet: header at dword143,
register offset0x318 at144, differing value at149, register0x028c70.
`ac_init_gfx6_cb_surface` calls upstream `ac_colorformat_endian_swap`, which
returns ENDIAN_8IN32 for COLOR_8_8_8_8 on a BE host. This is an existing explicit
format contract, not a missing translation or an arbitrary ignored difference.

Complete shader executable comparison from the previous pass also matched for
this test; its five non-executed UMR marker differences remain documented in
../mesa-3d-contracts-20261109/README.md. These results do not prove correct GPU
execution, but do not support adding further blanket swaps to this workload.

## Method and limits

Default-off TABOR_IB_CAPTURE_DIR instrumentation records two files per completed
GFX chunk: canonical LE encoding of final native construction, and actual bytes
at publication. Capture happens after size/chain fixups, padding and optional
NOP replacement. It adds no GPU commands or allocation-policy changes.

Both native and SPE builds pass. Standard Piglit, EGL, libdrm and the same
Mesa source are used; the SPE backend uses the previously documented offline
Trixie time64 adapter. No physical GPU device is available to the runs. Zero
pixel results are expected because the no-op backend does not execute commands.

The captured profile is Polaris12, not the actual Polaris11 board. Its selector
correctly leaves the existing Polaris11-only TABOR_POLARIS11_LE_IB opt-in
inactive: actual published SPE bytes remain native BE, while the canonical
files encode construction values LE for comparison. The comparison explicitly
checks and reports this; it does not claim the no-op run exercised the physical
kernel013 LE/swap0 pairing. Existing actual-source serializer fixtures and
physical Polaris11 publication traces are separate evidence.

Only one main IB is emitted in this test. Although the hook covers previous
chunks, this run does not exercise chains, preambles or reset-NOP paths.
Addresses happen to match across these runs; no address normalization was used.
All 400 words are compared; the sole expected difference is decoded and asserted.

## Remaining publication distinction / next hardware plan

Source: amdgpu_ib_new_buffer allocates GTT command memory without
RADEON_FLAG_GTT_WC. amdgpu_bo_create adds CPU_GTT_USWC only when that flag is
present. Kernel amdgpu_ttm_tt_create selects ttm_cached versus
ttm_write_combined from the flag; amdgpu_ttm_tt_pde_flags also derives SNOOPED
from cached memory. Thus changing this policy changes both CPU mapping and GPU
page-table coherency attributes. A memory barrier is not proof of cache cleaning.

The accepted explicit-LE/swap0 WRITE_DATA test used USWC, with actual marker,
fence and remap validation. An equivalent cached LE/swap0 case has not passed.
Earlier cached tests used a different fetch-swap setting and are not a control
for this remaining question. Do not claim a cache bug is proven.

After a clean boot and read-only root/module/hash checks, the next discriminating
trial should use the already-qualified allocated-buffer WRITE_DATA binary with
identical LE packets, kernel013 swap0, queue, addresses/alignment and marker
checks, varying only cached versus USWC allocation policy. Retain actual
allocation flags, fence and marker/remap bytes plus off-board kernel logs.
Stop immediately on a failure/recovery; do not proceed into GL or reload the
module. Even a timeout cannot guarantee recovery from a bus/kernel hang.

If only USWC passes, qualify a narrowly gated shared GFX-IB allocation-policy
candidate before another standard point draw. If both pass, do not change cache
policy merely because it was suspected: retain evidence and inspect shader/
render-target visibility separately. No production cache-policy patch was
added based solely on this source review.

## Reproduction / provenance

prepare.py adds capture hook to the private candidate. build-spe.py and
build-native.py reuse pinned environments with 2 CPUs/4GiB, network disabled;
heavy jobs ran sequentially on R730. run-spe.py uses PrivateDevices and bounded
QEMU, run-native.py uses a container with no physical GPU. compare.py checks
complete streams and the decoded register difference. evidence/ retains the
patch, before/after source hashes, launch/build/run receipts and raw captures.
The private offline libgallium was refreshed; no installed board runtime changed.

### Hardware preflight: waiting for fresh boot

User authorized the control trial. SSH reached kernel013, taint0, rootRO and the
expected module hash, but boot645ccbbf-c51a-4a08-83e1-c53c7369761a retains GPU
cleanup tasks blocked on fences from the prior shader failure. Saved the kernel
log before restarting. `sync; /sbin/reboot` returned127: this rescue image has
no reboot command, PID1 is sh. No forced reset, sysrq or test submission followed.
User needs to power-cycle and select the normal Linux entry.

run-cache-control.py refuses that failed boot ID and checks kernel/module/root,
parameter and kernel-error state. It stages the already-accepted binary and
existing bounded launcher into /run only. Run USWC+LE control first, then cached+LE
only if successful and kernel remains clean; stop immediately on any failure.
It does not run GL, reload the driver or reset the GPU. The two recovered
volatile artifacts are saved locally under /tmp/tabor-cache-control-artifacts
for restaging after boot; the script verifies the accepted test hash and remote
copies. The script has syntax validation; hardware execution is still pending.

### Physical cached/USWC control: both PASS

Fresh boot178dae6d-2771-4fa4-8709-a91f770b0712. The established installed013
first-bind procedure verified the module hash and loader option, remounted root
RO before binding, and enabled polaris11_le_user_ib=Y. Off-board /dev/kmsg logs
are retained. No reload or GPU reset occurred.

Same accepted gfx-write binary SHA903df0d059684808a6f4616adaa7a709e76477fb69b0da5cc444a43a722accdf,
same explicit-LE8DW packets, VA0x10000, marker0x10800, kernel GFX fetchswap0:

| GTT CPU allocation | flags | Fence | Marker/remap | Result |
| --- | --- | --- | --- | --- |
| USWC | 5 | complete | addefeca / addefeca | PASS |
| cached | 1 | complete | addefeca / addefeca | PASS |

Post-test boot ID unchanged, taint0, amdgpudrmfb registered, rootRO, SSH responsive.
No GPU reset/hang reported by the guarded checks. Optional debugfs fence-info
read was unavailable because debugfs was not mounted; it is not an acceptance
claim. Missing /usr/share/libdrm/amdgpu.ids is a human-readable-name warning;
actual allocated/submitted/fenced/verified writes passed.

This qualifies basic cached GTT LE-IB fetch and response for this small control.
It does not prove visibility for larger command buffers, shader uploads, render
surfaces or concurrent workloads. The result does not justify a cache-policy
change. No GL test was launched. Next audit should follow actual shader execution
and render-target memory publication/response, retaining this negative control
against an unproven general cached-IB hypothesis.
