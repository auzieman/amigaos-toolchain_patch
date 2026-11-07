# Polaris11 control/compute command-memory encoding

Follow-up to physically passing GFX ring, maintaining the target-specific contract.
Predicate now includes GFX, KIQ and COMPUTE on BE Polaris11. All use the already
validated single/bulk/NOP/patch writers and LE pointer shadows. HQD queue swap is
off for this contract. Native CPU MQD initialization and register commits remain
native; native reset backups are taken before converting the complete GPU-visible
vi_mqd_allocation to LE once at each queue-init boundary, including restore paths.
vi_mqd_allocation contains a u32-field vi_mqd and4additionalu32 fields.
IB command memory remains a separate native+IB-swap contract, not yet accepted.

Fresh isolated6.12.113 modules build exit0, unchanged .config/Module.symvers,
4CPU/6GiB/network-none and exact ordered patches. Artifact SHA256
403837663941f14ed2b2daf83847786074f3290f01e106f86a86855f2a504732.
Physical acceptance pending. No disk-module or boot-default changes.

## Physical attempt: inconclusive, board unresponsive

Candidate upload/hash check and initial continuous kmsg capture succeeded.
Combined rmmod-old/insmod-new command produced no result before45s timeout;
subsequent bounded SSH health check also timed out. Capture cleanup could not
fetch kmsg. Cannot distinguish prior failed-probe unload from new candidate
initialization. No KIQ/compute/display acceptance claimed. Need fresh physical
power-cycle and first insertion of this candidate, not another warm chained test.
Candidate remains /root/gfx-queues-le-hardware-20261106-001/amdgpu-candidate.ko;
disk module and boot defaults unchanged. Previous GFX-only hardware pass retains
its independent saved logs and source-qualified call ordering.

## Fresh boot follow-up

Fresh physical boot confirmed6.12.113-tabor-modular, uptime34.61s, no modules
loaded and SSH working. First-load script run then exceeded60s; subsequent
SSH banner exchange and edge ICMP checks failed. User reports green display.
No stdout or remote kmsg obtained; cannot localize dependency-load, held module
insertion or explicit GPU bind. This is an unsuccessful fresh-boot attempt,
not display acceptance, and does not isolate MQD versus queue encoding.
Previous assumption that warm unload alone explained hang is insufficient.
Add explicit stage output and off-board live kmsg capture before another bind.
A later laptop screenshot was of a different desktop view, not verified VLC;
do not use it as GPU output evidence. No further board writes attempted.
