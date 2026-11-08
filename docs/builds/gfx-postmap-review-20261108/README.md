# Bounded6.12 architecture and build review —2026-11-08

Result: candidate module builds under normal Kbuild and passes ELF/vermagic and
all687 imported-symbol CRC checks against the accepted6.12.113-tabor-modular
export table. No GPU load, reset, kernel update or boot-file change. Physical
GPU initialization remains unproven; this is a usable test artifact, not a
claimed solution of the remaining PCIe fault.

## Communication problem, not another global byte swap

The working control uses the same card on x86_64 Linux6.12.94, while the A1222
uses PPC32 BE Linux6.12.113. There is no captured POWER8/9 hardware control in
this project. A ppc64le example cannot establish correctness of a BE serialized
buffer: native LE loads can hide missing conversions that fail on BE. A PPC64
BE comparison also needs its actual PCI/DMA/coherency setup, not CPU branding.

Architecture checks against pinned6.12 source and its actual compiled module:

* MMIO/doorbell writel already performs LE output. The compiled doorbell writer
  contains hwsync followed by stwbrx. No missing generic PPC byte-swap layer was
  found on that path. Normal MMIO register values must remain CPU-native.
* RLC register-list/restore firmware data is normalized with le32_to_cpu by the
  existing loader before the native parser/MMIO loop. Converting it again at
  that loop would double-swap it. GPU-visible CSB data is a distinct LE buffer.
* Legacy Radeon BUF_SWAP_32BIT=(2<<16) and gfx8 REG_SET_FIELD(...,BUF_SWAP,1)
  encode the same0x20000 bits because gfx8 field SHIFT is17. Replacing1 with2
  based on another field's enum would be an unjustified change.
* FSL PCI setup requests inbound read/write snooping; that source setting is
  not a measurement of live DMA coherency. Prior successful KIQ scratch and
  GPU readback checks demonstrate some working transport, not every engine.

Existing restored boundaries remain meaningful source fixes: raw LE SMU payload
words are decoded before MMIO; native transfer metadata is serialized for the
GPU; native MQD staging is kept apart from IO-safe GPU publication. Those are
separate documented formats. Do not hide the unknown next fault with another
blanket conversion, skipped ring test or disabled IP block.

NXP TechSupport identifies P1022 ERR_DR0x00800000 as a completion timeout for
an outbound non-posted request. Thus the captured fault concerns an unanswered
host transaction, not proof that a particular SMU message has the wrong bytes.
Our capture has different accompanying status values from the vendor example;
only the identified ERR_DR bit is used here.
Primary source:
https://community.nxp.com/t5/PowerQUICC-Processors/P1022-Console-hangs-after-PCIE-error-dump/m-p/1364368/highlight/true

That gives the next code-review objective: find the producer/state transition
that precedes loss of endpoint responses. A timeout can be a consequence of a
wedged GPU and does not establish a host-bridge root cause. Current entry/result
markers distinguish GFX, KIQ, compute, GUI-idle enable and later SDMA/IP setup.
Use that boundary and a matched little-endian control before changing another
serialization contract. The upstream posted-write flush and compute-test error
propagation are real code corrections; their impact on this hang is untested.

## Build repair and checks

The previous single-module invocation failed modpost: in-tree Linux6.12 consumes
vmlinux.o and module-provider objects, rather than using the copied Module.symvers
like an external-module build. No missing symbols were ignored or fabricated.
A private copy of the complete accepted Kbuild output was paired with the fresh
re-patched source through the same path layout; normal make modules completed
exit0, bounded4 CPUs/6GiB/network-none. Accepted originals and SDK stay untouched.

build-003.py records the exact recipe. build-003.json/log retain the result.
Module SHA256080f54935bb910a9bafa021b8e12ac8965aab34344cbb382067c2b18d032eb72.
Config remains7effb33413cbb4ab6dcda93563c2600f1948f9764387df70cd016883892fdaec.
Verification recorded687 imported symbol entries for both the installed
baseline and candidate. Exact results are in the receipts.

scripts/verify-ppc32-module.py checks actual ELF32 BE/PPC/REL identity, full
vermagic flags against the installed reference and each imported CRC against the
accepted export table, including module_layout. Positive control: the module
fetched from the live board passes that export table. Wrong release and a
one-bit module_layout CRC mutation are rejected. This does not certify every
kernel setting or hardware behavior. Patch14/15 replay on the three parent
files matches the compiled source byte-for-byte; hashes are in
qualification-controls.json. No local compilation or source extraction.

Candidate is hash-verified in an inactive private directory on A1222 (see
inactive-board-staging.json). Original installed module and healthy dual-core
kernel are retained. Next hardware action is one controlled first bind with
protected root and off-board logs; no automatic test has been started.
