# GPU-side descriptor readback diagnostic

Parent native-MQD-staging002; excludes negative compute-VRAM placement patch.
Pre-map KIQ self-test retained. Added COPY_DATA GPU->writeback calibration from
immediate1234abcd, then eleven stable MQD fields from KIQ VRAM and first compute
GTT descriptor, compared to native CPU backup. Logs GPU result, expected value,
source address, offset and actual writeback bytes. Header/base/control/report/EOP
addresses sampled, excluding changing read/write pointers. First mismatch returns
EIO through existing initialization error path, not a fabricated success. All
existing tests remain. Passing samples do not prove every descriptor field or
cache path, and a timeout is not automatically an endian diagnosis.

Packet format checked against AMD GPUOpen PAL gfx6 SI/CI/VI definitions and
BuildCopyData at pinned2de164b431f8a27652e63513ae73338dc512e5bf; source hashes/URLs
retained. Six dwords: header, source selector1(memory)/5(immediate), destination5,
write-confirmbit20, source/destination low/high. Linux gfx8 emit_rreg uses same
packet/writeback destination convention. Calibration must pass before interpreting
memory-read evidence. Existing validated LE ring writer supplies packet encoding.

Fresh isolated R730 gfx-mqd-read-20261106-001, pinned6.12.113 source/config,
ordered patches,4CPU/6GiB/network-none. Build/physical outcomes pending.

Build completed exit0; config/Module.symvers identical to modular003. SHA256ed5b746997cdaab551ac75d8cfc323391708ea9305a386f8e0d4ebe9bce57169. Local ignored artifact amdgpu-gfx-mqd-read.ko ready; hardware test pending cold boot.

## Physical result, reviewed November7

Off-board006 confirms KIQ scratch test0 and GPU writeback calibration1234abcd
with bytescd ab3412. GPU COPY_DATA reads all11sampled words of KIQ VRAM MQD and
first compute GTT MQD correctly against native backups (22/22); contract result0.
Mapping submission follows, then same PCIe00800000/23 storm and SSH loss.
This directly demonstrates the sampled publication/read/writeback chain works.
Do not keep attributing the remaining failure to unproved descriptor byte swaps.
Only22words/2descriptors checked, not full object semantics or all consumers.

November7 source audit: tonga_ih/iceland_ih decode each IV dword/writeback through
le32_to_cpu; gfx8 CSB producer already emits cpu_to_le32 for each command.
These are established proper conversions, not new patch targets. Raw BE IB and
shader producers remain a later separate acceptance issue; not established cause
of the pre-IB mapping failure. Staged SET_RESOURCES and per-queue MAP diagnostics
will separate the currently combined submission without disabling normal tests.
