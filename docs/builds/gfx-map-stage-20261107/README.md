# Mapping-command stage gates

Parent gfx-mqd-read001: retain verified software-LE rings, native/IO-safe MQD
publication and pre-map GPU readback. For BE Polaris11 only, submit SET_RESOURCES
separately, run normal KIQ scratch self-test, then submit each MAP_QUEUES with its
own allocation/commit and another normal KIQ scratch self-test. Log mask and
queueME/pipe/slot/doorbell/descriptor/writeback addresses. Normal final GFX/KIQ/
compute tests remain. Other platforms retain existing batch. No new conversions,
resource-mask changes or queue omissions. This diagnostic changes initialization
submission boundaries; passing alone would not establish the previous cause.

Fresh R730 isolated gfx-map-stage-20261107-001, cached pinned6.12.113,
4CPU/6GiB/network-none and accepted modular config. Build/physical pending.
A1222 confirmed freshly booted/no modules before preparation; leave unloaded
until capture and exact artifact checks are ready.

## Physical result

Module4f80e4c7b132f581618973ff1a4910c4c7e10e5fd0d8cdf3428ee2e27e8ff528,
fresh physical kernel/no modules, verified transfer/rootro/off-board capture.
KIQ and GPU readback calibration/samples pass. SET_RESOURCES maskff/8queues
returns self-test0. All8individual MAP_QUEUES calls each followed by self-test0;
all submissions completed marker emitted. Then PCIe storm/lost SSH during later
initialization. This moves the observed failure beyond the stage checks; does not
prove async queue state fully usable or establish why original batch failed.
User reports purple/magenta. No framebuffer/accelerated desktop acceptance.
Next identify which normal post-mapping ring test or later init stage fails;
retain proven GPU byte-readback evidence and avoid speculative extra swapping.
