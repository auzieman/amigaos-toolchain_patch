# GFX8 swap contract: immediate hardware readbacks

Diagnostic only: add readbacks immediately after each CP_RB0_CNTL setup write,
and after CP startup. No encoding/reset behavior changed. Builds on the previous
LE SMU upload, LE transfer-TOC boundary and producer snapshot experiment.
Fresh isolated R730 gfx-swap-readback-20261106-001, constrained4CPU/6GiB,
network disabled. Modules build exit0; .config and Module.symvers byte-identical
to accepted modular kernel003. Module SHA256:
be6d92598893bed21b86d1262665299cdfe16612f59148f6a0065c31dcfc6574.

## Newer upstream check

Pinned torvalds/linux d48723711bae9b8cdc56719c448ba42fef28cbee;
full fetched-file hashes in upstream.json, bounded source excerpts retained.
Current gfx8 still enables BUF_SWAP1 on BE, writes native ring words and native
pointer shadows, and retains XXX swapping comments. Common clear/write/bulk
paths remain native stores/memcpy. No coherent software-LE replacement found
in these current paths. Reviewed100 gfx_v8_0.c path commit subjects spanning
2020-08-24 through2026-09-10 (recent-history.json); no endian/swap fix identified.
This is a bounded source/history check, not proof no downstream fix exists.
Recent compute-ring reset/error changes do not establish a graphics-ring endian fix.

## Physical result

All three immediate readbacks omit exactly BUF_SWAP bit17:

| Phase | Written | Immediately read |
|---|---|---|
| Initial |0043880a|0041880a|
| Pointer-write enable |8043880a|8041880a|
| Final |0043880a|0041880a|

After CP startup:0041880a again. The pointer-write-enable bit31 does read back
when set, while swap bit17 never does. This localizes the observed loss to the
write/read boundary, rather than a later startup writer. It strongly supports
an unavailable/ineffective swap setting on this ASIC; register readback alone
is not a complete hardware-specification proof of fetch behavior.
NativeBE ring packet bytes remain c0 01 79 00 /00 00 00 40 /de ad be ef.
Scratch remainscafedead, CP_RPTR88, CP_WPTR500; gfx self-test fails-110.
No framebuffer/device binding. SSH healthy; module insertion returning0 is not
successful GPU initialization.

Next experiment should establish a coherent little-endian GFX8 producer contract
(single/bulk/NOP/patch/IB writes plus pointer writeback), with hardware swap off,
not bypass the ring test or replace individual packet constants. Audit other ring
families separately to preserve their existing swap contracts and x86 output.
 Installed module tree remains unchanged;
this is a temporary in-memory candidate, not a new boot default.
