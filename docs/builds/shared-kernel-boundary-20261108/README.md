# Shared kernel boundary review — 2026-11-08

The installed e2e-001 AMDGPU object retains PowerPC byte-reversing MMIO loads and stores (`lwbrx`/`stwbrx`). This does not support a claim that the common MMIO endian implementation was removed.

A separate ASIC clock caller in `amdgpu_atombios_get_clock_dividers` still assigns converted values to native 24-bit bitfields for ATOM revisions 4 and 6. Earlier patch 0020 corrected the PowerPlay callers but not this caller. Candidate 0022 centralizes full-word little-endian packing and decoding in atom.h and updates both caller families.

The actual ASIC clock routine was extracted and tested against a mock ATOM endpoint: 56 request/response cases per architecture, plus error propagation. The old PPC result differs from x86; corrected PPC matches unchanged x86. See tests.json and test_contracts.py. Freestanding x86 fixtures explicitly realign their syscall-entry stack; PPC uses qemu-ppc. This is a serialization test, not a hardware or VBIOS execution test.

The actual card command-table revision is not yet established. The candidate has passed patch application checks and these tests, but has not been built into a complete kernel or tested on hardware. No firmware, boot media, or running GPU was changed during this review. The last physical failure remains the UVD-stage PCIe fault documented in ../e2e-usb-20261108/.

## Historical patch coverage and conversion ownership

Re-read retained `work/polaris-history-20261105/amd_powerplay_be.patch` (SHA283feb087ae1f32c16726045dd689b2258abdbee50c89b7fa8d8ca514d210b2c). Its clock-bitfield helper and caller corrections are confined to `powerplay/hwmgr/ppatomctrl.c`; it does not patch `amdgpu/amdgpu_atombios.c`. Our initial 0020 mirrored that coverage limitation. Thus the duplicate ASIC clock interface is a demonstrated omission in both patch sets, not evidence that all PCIe communication is incorrectly swapped.

| Boundary in current e2e-001 source | Encoding owner | Review result |
| --- | --- | --- |
| Register/MMIO | Linux readl/writel and PPC accessors | Compiled byte-reversing instructions verified; do not add another swap |
| GFX/KIQ/compute ring memory | Shared software ring writer, hardware swap disabled by 0007/0008 | Single/bulk/clear writers covered; full IB/shader acceptance remains separate |
| UVD ring and IB fetch | Native CPU words plus UVD_LMI_SWAP_CNTL=0xa on BE | Existing hardware-swap contract retained; effectiveness on this card not measured |
| SDMA ring/IB/writeback | Native data plus dedicated hardware swap bits | Existing contract retained; not automatically equivalent to UVD/GFX |
| ATOM clock parameter words | Caller serialization and interpreter LE access | Historical and initial local patch missed second caller family; 0022 shares packing/decoding |
| SMU AVFS calibration | Explicit SMC big-endian wire constants | Device protocol differs from ATOM LE; universal little-endian conversion would break it |

The key integration question is conversion ownership across each complete path: CPU representation -> publication -> hardware fetch conversion -> response/writeback decoding. Different paths need not share an encoding, but each must preserve its specified device-visible values. Hardware swapping and software conversion must not both be applied to the same transfer. The current source confirms mixed strategies, not a demonstrated double swap in UVD. No change to UVD swap controls is justified by the graphics-engine readback alone.

The first UVD test issues a direct MMIO context write before allocating/submitting its two-word ring packet. Existing timestamps do not isolate that direct access from packet execution. It is premature to label the first failure a malformed UVD packet; capture those distinct boundaries in a reviewed candidate before changing the shared ring policy.

## Physical CPU-only gate

`test_on_board.py` stages the original and corrected freestanding PPC fixtures in existing tmpfs /run, verifies their hashes, and compares outputs to the retained x86 reference. It requires a fresh boot without AMDGPU loaded and never binds or accesses the GPU. First connection attempt returned no route to host; no fixture ran on hardware. This gate tests CPU serialization only; a subsequent discriminating GPU transfer test remains required.

Physical CPU gate passed on fresh 6.12.113-tabor-e2e-001 A1222: all 56 corrected cases match the x86 reference; original routine mismatches as expected. Both executables ran from a private 2MiB tmpfs after hash verification. No AMDGPU load, GPU access, boot change or display acceptance. Full receipts/output in physical-cpu-001/. This tests real PPC execution against a mock ATOM endpoint, not the card interpreter.

## Scope correction: whole host/device boundary

The user explicitly requests coverage of the bus/driver integration, not acceptance based on clock serialization alone. Candidate e2e-002 completed full kernel/modules/DTB compilation and bundle verification, including 43 modules and 687 AMDGPU imported-symbol CRCs. It is not deployed or hardware validated. Module SHAa8093090ece8c23e2116b71b41d79da777aeb23785c6f3fdaceee7d928e726e6.

The broader acceptance ledger remains:

1. PCI configuration and BAR CPU/bus addresses: trace host-bridge ranges and resource translation; earlier outbound-window correspondence is evidence only for that map.
2. MMIO access: trace direct/indexed register operations through readl/writel and PPC accessors; compiled byte reversal verified, individual failing access unresolved.
3. DMA addressing: trace DMA mask, coherent allocation/mapping, inbound windows/SWIOTLB and GPU-visible address generation; outbound BAR correctness does not validate inbound DMA.
4. Publication/coherency: identify VRAM I/O versus ordinary/coherent RAM mappings and the barriers/flushes before doorbell or write-pointer publication.
5. Device formats and return path: ring/IB/descriptors, firmware tables, writeback/fences and interrupts each require one matching serialization/decoding contract; no universal byte-swap layer is assumed.
6. Physical fault discrimination: distinguish the first UVD direct register access from command publication and completion before attributing the PCIe error to packet decoding.

The 22 clock-helper call sites and 56 mock-endpoint cases cover only the ATOM clock format. They do not close the DMA, PCIe, coherency or complete GPU response contracts above. No claim of a fully translated/working bus follows from e2e-002 build success.

## Passive PCI hardware baseline

Read-only PCI config/sysfs comparison passed on the unbound card (1002:67ff). Vendor/device/class/revision decode matches kernel attributes. BAR0 bus e0000000 maps to CPU c40000000; BAR2 f0000000 to c50000000; BAR5 f0200000 to c50200000, all memory examples sharing offset b60000000. These distinct address domains are expected host-bridge translation, not evidence of corruption. I/O BAR4 is1000. SSH survived; no GPU BAR MMIO, config writes, module load or ATOM execution. The new clock fix was not exercised. First attempt found dd unavailable in minimal userspace; corrected collection used read-only sysfs cat and retained the first64 bytes. See passive-pci-001/.

## Live installation of verified candidate

Complete e2e-002 kernel/modules installed via SSH with identified USB serial and hash verification. New versioned boot/e2e-002 payload and module-release directory preserve e2e-001 files. Existing firmware bytes verified without replacing aliases. Boot script selected only after payload readback; exact prior selection retained as /boot-e2e001-rollback.scr. FAT synced and unmounted. No GPU load or reboot performed; physical boot and initialization pending. This deploys the real shared ATOM fix, not the standalone simulated consumer or a complete universal GPU translator. See live-deploy.json and deploy_live.py.
