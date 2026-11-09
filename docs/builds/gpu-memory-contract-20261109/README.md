# Allocated-buffer path audit — 2026-11-09

Physical kernel012 remains untainted, SSH responsive; no module reload/reset.
The narrow GFX WRITE_DATA helper is based on upstream libdrm test packets and
writes only its allocated4KiB BO. It is not a graphics/stress workload.

Controls: nativeBE and explicitLE command bytes in VRAM both return completed
fences with zero data. Unmap/remap does not reveal a marker. GTT with the
CPU_GTT_USWC flag also fails. Explicit seqno1/IBcount1 exclude libdrm's empty
submission shortcut. Kernel ioctl, not a userspace GPU-written user-fence
shortcut, supplies the fence wait result. This does not prove IB execution.

A dedicated tracefs instance records VM set/copy/flush and CS ioctl events.
The captured test uses direct WRITE_PTE, not the copied PTE array fixed in012.
No trace overruns or dropped events. Tracing/events are disabled afterward;
the small disabled instance remains because the target's BusyBox has no rmdir.
Do not retry cleanup by recursively deleting tracefs contents.

Held allocations permit eight-byte read-only VRAM inspections using the driver
amdgpu_vram node, with addresses from the current trace. On PPC32 the handler
uses MM_INDEX/MM_DATA register access and returns native CPU uint32 values;
LOW/HIGH outputs are decoded dwords, not a purported raw-memory byte stream.
GTT PTE00000000d749f077 matches the traced address/flags. Its PDE is
000000f4fffda001 and matches the traced leaf table. VMID7 page-table register
0x556 reads0x0f4fffa0, matching pd_addr0xf4fffa0000 >>12. Source register numbers
come from gmc_8_1_d.h. Only this VM register is read; no register values written
by the diagnostic helper. Indexed VRAM reads use the kernel's normal API.

A held VRAM allocation has PTE0000000000384071, matching the VRAM-relative
address/flags. Direct VRAM reads at offset384000 show the native-BE IB as GPU
little-endian dwords003703c0/00051000, matching its CPU bytesc0033700/00100500.
The target at offset384800 is zero even via direct indexed VRAM read. Hence
this observation is not merely a stale ordinary CPU mmap read. A first attempt
incorrectly subtracted the GPU VRAM base from an already-relative VRAM PTE
address; the kernel rejected the negative read offset. The corrected test
asserts address domain/range and reads the appropriate relative offsets.

CPU command-ring dump has matching read/write/software pointers1280. The
latest recorded GTT job's IB packet at1095 is c0023f00,00010002,00000000,07000008:
VA10000 plus legacy swap2, VMID7,8dwords. Its root-register write requests the
correct0f4fffa0. The ring packet bytes are software-LE; do not swap those again.
This dump predates the later held VRAM control; keep the contexts distinct.

The surviving untested combination is explicit-LE userspace IB bytes with
fetch swap0. Both existing userspace tests use fetchswap2; changing the bytes
alone did not change that setting. The passing kernel-owned GFX self-test
uses explicitLE bytes plus swap0. The next bounded experiment is documented in
../user-ib-fetch-20261109/README.md. No declaration of full translation coverage
or a fixed hardware rendering path follows from these measurements.
