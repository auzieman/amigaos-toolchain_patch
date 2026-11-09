# GFX8 indirect-buffer completion review — 2026-11-08

Physical candidate007 already reaches readable fbcon and presents the verified
CPU/SPE fractal. Its later GFX IB timeout remains the acceleration gate. The
outer IB test loop stops at primary GFX failure: later engines were not
independently measured as IB failures. Preserve the working display.

Source flow is IB allocation -> scheduler dispatch -> primary ring IB descriptor
-> commit/publication -> GPU IB fetch -> WRITE_DATA -> EOP/RELEASE_MEM fence
write -> IH/fence processing -> waiter -> payload comparison. Common scheduling
has a publication barrier and HDP operations. GFX/compute descriptors explicitly
request BE 32-bit fetch swapping; SDMA selects its own IB swap control. Primary
ring LE encoding, IB fetch order, fence memory and interrupt records have
distinct contracts. Do not globally swap all buffers or reuse the primary-ring
conversion for native IBs while leaving hardware fetch swapping enabled.

Confirmed defect: the shared GFX/compute IB test compares a GPU-written LE
writeback word as native u32. Its initializer and the fence reader already use
LE conversions; SDMA's equivalent comparison decodes correctly. Patch0028
uses le32_to_cpu(READ_ONCE(...)). This prevents a false EINVAL **after** successful
completion; it does not explain the existing earlier timeout.

On timeout, patch0028 additionally records CPU-visible payload/fence memory,
sequence counters and IB address/length, before freeing the resources. It adds
no register reads, commands or reset/recovery. That discriminates a completed
memory write with missing wakeup from an uncompleted payload/fence operation;
it does not independently prove DMA visibility, IRQ delivery or execution.

`review.py` extracts the actual ring writer, GFX/compute IB/fence emitters,
CPU fence decoder and original/fixed test caller from pinned candidate007.
512 cases per architecture pass on x86 and PPC32BE/QEMU: ring wrap, engines,
fence sequences, old/corrected callers, missing fetch swap, double swap, and
completed-memory/no-wakeup model. Selected output bytes match across CPUs.
Allocation, scheduling, GPU behavior and fence wakeup are modeled. This is
not a GPU emulator or hardware acceptance. Source/header hashes and limitations
are retained in receipt.json. Initial QEMU launch failed because the 3GiB
virtual-address cap excluded its 4GiB guest reservation; a 6GiB virtual cap fixes
the fixture runner, not driver code. Execution remains one CPU on R730.

Fresh matched candidate `6.12.113-tabor-e2e-008` built on R730 under two CPUs/4GiB.
43 modules, ELF32BE, full vermagic and all 687 imported symbol CRCs pass.
AMDGPU SHA256: 6fd480b5ca4c0bbd22c1aa98d0cbed4d2fb52373d474918d033f9ff9efcae4f4.
See build-receipt.json. No USB writes, reboot, GPU load, or physical GL pass.
This candidate remains staged; candidate007 is the hardware recovery reference.
