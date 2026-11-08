# Polaris interface closure review

The acceptance scope is the complete selected A1222/Polaris path, not a passing
ring or mailbox test. `ledger.json` identifies 22 owning contracts spanning
registers, firmware, state construction, rings, indirect buffers, page tables,
interrupts, DMA/cache publication and scanout. Each entry has a pinned-source
anchor and its actual qualification limits. None is promoted to complete
hardware acceptance by static inspection.

`audit.py` inventories candidate accesses throughout the pinned AMD source tree
on the R730. It finds 686 files with matches: 12,093 register-access lines,
2,370 ring-publication lines, 891 indirect-buffer-store lines, 9,325 endian
policy lines, 2,070 mapping/copy lines and 118 ordering lines. These overlap,
include other ASICs and inactive branches, and are NOT defect or coverage
counts. The full candidate list remains on the server in
`/srv/data1/tabor-build/source-review/interface-closure-20261108/source-candidates.json`.
Source file hashes are retained in audit-receipt.json. This is a searchable
review inventory, not a static correctness proof or exhaustive call graph.

## New actual-source qualification

`test_memory.py` extracts the actual fence read/write functions, CPU GART/PTE
writer and Tonga/Polaris interrupt decoder. Each architecture passes 256 cases
for each of fence memory, fence atomic fallback, 64-bit page-table writes with
surrounding sentinels, and interrupt decoding/byte-pointer advance: 1,024 checks
per architecture. All 47,616 emitted bytes match x86 and PPC32 BE/QEMU.

The page-table test models Linux writeq's LE MMIO contract; it does not execute
real MMIO or prove the P1022 mapping. The other functions retain their source
LE conversions. No changes to these already-correct encoders are warranted.
All nine aggregate suites pass; missing hardware contracts remain explicit in
the aggregate report and the overall gate remains BLOCKED.

## Paired contracts that must not be conflated

- GFX and compute primary ring software LE policy does not change IB storage.
  Both actual gfx_v8_0 emit_ib functions explicitly set BE indirect-fetch mode2
  in the address/control packet. A native IB is therefore not automatically a
  missing conversion. Shader fetch is another consumer and needs its own check.
- SDMA has separate RB_SWAP_ENABLE, RPTR_WRITEBACK_SWAP_ENABLE and
  IB_SWAP_ENABLE settings. Preserving those is essential when evaluating raw
  stores into SDMA indirect buffers.
- UVD decoder LMI_SWAP_CNTL0xa sets RB_MC_SWAP=2 and IB_MC_SWAP=2 (actual masks
  in uvd_6_0_sh_mask.h). The UVD encoder primary ring now passes with software
  LE. Its native create/destroy IB producers and firmware-driven fetch still
  need a paired consumer review: the encoder's use of the decoder LMI fields
  must not be guessed from the register names or primary-ring result.
- tonga_ih_decode_iv decodes all four input dwords with le32_to_cpu. In contrast,
  tonga_ih_set_rptr writes a native shadow value and has an explicit upstream
  "check if swapping is necessary on BE" TODO. Doorbell register access and
  shadow-memory access are different contracts. Identify the shadow consumer
  before replacing the store; the TODO alone is not a demonstrated defect.
- CPU GART writes use writeq; fences use LE memory; SMU transfer objects use BE
  fields; pixels use format-specific scanout swap. A single global swap would
  violate several existing contracts.

## Remaining closure work

Follow the ledger through actual selected callbacks and consumers: encoder IB
and VCE fetch, complete SMU tables/firmware copies, shader buffers, IH shadow,
P1022 DMA windows/cache visibility, publication ordering, and display formats.
Capture-dependent validation must explicitly record firmware/table inputs,
readback and first-failure boundaries. Static/offline checks can close encoding
proofs but cannot close the physical DMA/scanout gates.

No new kernel patch was justified in this pass. Existing0024 is still the
built state-clock correction. No GPU access, USB mount/write, install or reboot
was performed. This is broader qualification with remaining gaps exposed, not
an assertion that every interface has been fixed.

## UVD decoder and encoder expansion

`test_uvd_decoder.py` executes the actual amdgpu_uvd_get_create_msg,
amdgpu_uvd_get_destroy_msg and amdgpu_uvd_resume functions with mocked job/BO/IO
endpoints. Per architecture, 288 message scenarios check the full 4096-byte
LE buffers, direct/allocated BO selection and error propagation. Five resume
scenarios cover byte-exact raw microcode copy and zeroed tail, saved BO restore,
PSP skip/clear path, missing BO and harvested instance. The emitted1,048,960bytes
match x86/PPC; the large outputs stay on the server. These checks use a synthetic
valid header, not a physical firmware execution or full container validation.

`test_uvd_payloads.py` executes both actual UVD encoder create/destroy IB
producers across768scenarios/architecture:256successful payloads plus allocation
and submission errors, each with/without returned fence. Native command values,
addresses and cleanup/refcounts match. Two explicit modeled fetch consumers
show the distinction: x86 raw bytes match LE fetch; unchanged native PPC raw
bytes require byte-swapped fetch (or producer-side serialization instead).
The actual encoder firmware/LMI fetch routing remains UNRESOLVED. No hardware
swap behavior is invented to turn this source test into a GPU success claim.

UVD closure includes decoder/encoder primary rings, their separate indirect
buffers and message objects, VCPU firmware transfer, fence/IRQ completion,
clock/power transitions and suspend/resume. Existing physical ring passes cover
only those ring tests. Decoder payloads/firmware copies now have source-level
byte checks; encoder IB consumer pairing, actual firmware execution, completion
and playback remain hardware/source review gates.

The expanded aggregate has eleven passing suites and still explicitly blocks
complete hardware acceptance. No additional driver patch or USB deployment was
made in this review.
