# Producer-first driver audit and timeout snapshot

Reviewed current source, not another data-conversion change. CONFIG_CPU_BIG_ENDIAN=y;
Linux big_endian.h supplies swapping cpu_to_le helpers. Register/doorbell writes use
writel. GART PTE writer uses writeq via io-64-nonatomic-lo-hi fallback on32bit, which
writes little-endian low then high dwords. Ring write/clear/bulk-copy produce native
words and gfx8 requests CP_RB0_CNTL.BUF_SWAP=1. Observed earlier control write
0043880a confirms that BE branch selected; it is not simply compiled as x86.
Ring commit has mb before pointer submission. Native pointer shadows still carry
XXX check if swapping is necessary on BE comments in gfx8 (and other generations).

Snapshot-only patch0005-gfx8-producer-contract-snapshot adds no conversions or reset
changes. Fresh constrained R730 buildgfx-producer-20261106-001 exit0, exact physical
config and Module.symvers compare pass. ModuleSHA256
61b73402e5a2407195638e9948268a5ca8aa134bc0c6b2c4d071dd2bc7e0514e.
Physical warm test reaches gfx ring self-test, fails-110, no framebuffer, SSH healthy.
Installed module files unchanged. Logged before failed-init cleanup:

ring GPUaddrff00609000; start1024, wptr1280/500; doorbell enabled/index32.
CP_RB0_CNTL0041880a: BUF_SWAP mask60000 shift17 decodes0.
CP_RB0_RPTR88, CP_RB0_WPTR500; CP_STAT94008200, GRBM_STATUSa0003028.
writeback rptr0, wptr native500 / LE-decoded50000.
Packet native values c0017900,40,deadbeef; actual bytes c0 01 79 00 / 00 00 00 40 /
de ad be ef. GPU-facing contract therefore relies on a swap that is not active in
this sampled control readback. Earlier requested control0043880a decodes swap1.
Source gfx8 has only the three setup writes of that constructed control value;
hardware clearing, unsupported behavior or an unobserved writer remain to qualify.
Do not assert register meaning from unrelated texture-endian enums.

GART page1545, PTE lowd767a077 high0. CPU page address and DMA-coherency mapping not
yet correlated; do not call this PTE proven correct. PCIe error header again saved.

This is a producer/consumer contract mismatch lead, not proof every failure has one
cause. Next correction must select one coherent ring encoding strategy, covering
single/bulk/NOP/patch writers, pointer shadows and hardware swap settings together;
a generic cpu_to_le32 in only ring_write would leave bypass paths and risk double
swapping rings that already use hardware conversion. First qualify swap write/readback
and buffer-fetch mapping; preserve legacy x86 output and other ASIC/ring contracts.
