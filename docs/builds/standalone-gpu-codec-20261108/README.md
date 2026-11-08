# Standalone GPU byte-contract interpreter

This freestanding userspace test extracts eight functions from the pinned e2e-002 driver: seven shared ring helpers and the actual UVD register-write ring test. No kernel module, GPU BAR mapping, register access or command submission is performed. MMIO context state, ring reservation/commit, device fetch and optional hardware byte swapping are simulated. Driver source notices remain in the retained template; generated extracts inherit that source's license.

Thirty-two cases per architecture exercise four conversion policies at eight ring offsets, including wrapping:

- Native memory plus hardware swap.
- Software little-endian encoding without hardware swap.
- Missing conversion.
- Double conversion.

On BE PPC the first two succeed; the negative controls time out against the simulated consumer. On LE x86 the architecture-dependent swaps are inactive and all policies preserve the native LE stream. The test checks those different expected outcomes explicitly. Additional checks exercise actual bulk writer, NOP clear, conditional packet patch, condition shadow, wrap and accounting behavior.

GCC native x86 and static PPC/qemu-ppc runs pass. The exact PPC executable also passes on the real A1222 CPU and reproduces its QEMU output byte-for-byte; SHA cb94d60053a1f5dbe57a62a2778c02252ec7813ede0b8d422e3717d588a35f44. Executed from verified private tmpfs with AMDGPU unloaded. See receipt.json and physical-receipt.json.

This widens the earlier 56-case ATOM clock request/response suite in ../shared-kernel-boundary-20261108/. It is a byte-contract interpreter, not a GPU or PCIe emulator. It does not prove that the card honors a hardware swap setting. Descriptor publication, DMA/coherency, interrupt/fence decoding, shader formats and a broader packet grammar remain outside this first executable. Do not use it to declare the hardware hang fixed.

Reproduce on R730 with run.py and ring-fixture-template.c in /home/owner/standalone-gpu-codec-20261108. Sources are extracted from the isolated pinned /srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-002/source. Results are retained under /srv/data1/tabor-build/source-review/standalone-gpu-codec-20261108. Host-only compilation and emulation belong on R730; the laptop does not compile or emulate.
