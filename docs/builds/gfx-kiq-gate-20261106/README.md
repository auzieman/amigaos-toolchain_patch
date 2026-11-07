# Pre-map KIQ self-test diagnostic

Experimental patch0009 adds the existing normal KIQ scratch self-test immediately
before resource/compute queue mapping for the software-LE Polaris11 target only.
A failure propagates normally. Existing later GFX/KIQ/compute tests remain.
Logs pre-map result, mapping submission entry/return; no added encoding/bypass.
Separates whether control-ring packet execution works from whether MQD mapping
causes the PCIe failure observed in off-board candidate002.

Fresh isolated R730 gfx-kiq-gate-20261106-001,4CPU/6GiB/network-none,
Linux6.12.113 original modular config, cached sources and ordered patches.
Build exit0; .config and Module.symvers compare exactly against modular003.
Module SHA256449ecd7d979904dfb619cea9e4f8dd530bf1ce237a0983ad426d37fd466420fb.
Local ignored artifact work/modular-usb-update-20261105-001/amdgpu-gfx-kiq-gate.ko.
Not transferred or hardware-tested: board locked after previous bind. Cold boot
required. Upload over SSH before root-ro handover, then use off-board capture with
explicit candidate path/hash. No USB move or boot-default edit required.

## Physical result

Fresh boot6.12.113-tabor-modular, no modules. Candidate transferred/hash verified,
SSH runtime logs off USB and root verifiedro. Off-board stage capture passes
held insertion. During bind: SMU response1/status3; pre-map KIQ self-test returns0.
Both mapping-submit markers emitted; PCIe00800000/23 storm and lost SSH follow.
Therefore real KIQ command execution passes; failure is triggered after compute
mapping submission. This narrows to mapping/descriptor/compute initialization,
not proof all descriptor bytes or DMA mappings are correct. User reports purple.
No display acceptance. Logs saved independently of target disk.
