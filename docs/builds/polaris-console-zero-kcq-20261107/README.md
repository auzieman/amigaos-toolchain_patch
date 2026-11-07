# Console isolation: zero kernel compute queues — 2026-11-07

Fresh physical A1222 boot, kernel 6.12.113-tabor-modular, untainted/no
AMDGPU loaded. Reused native-MQD-staging candidate002 (before GPU MQD-read
instrumentation, which requires at least one compute queue): SHA256
f6475b61ef7affae8fff7cbd008ef2a70090f96327f3c7a0cd8d2d9adb5e2e49.

Insmod explicitly supplied upstream num_kcq=0. Source review confirmed the
parameter accepts zero, MEC HPD allocation and compute-ring loops handle zero,
and the Carrizo-only EDC workaround does not execute on Polaris11. No new
firmware, kernel rebuild, module-tree replacement or boot-default change.

Off-board kmsg marker and read-only root mount verified before PCI binding.
Runtime SSH logging was moved off USB without changing authentication.
Pre-map KIQ scratch test returns0. Resource submission returns; then PCIe
ERR_DR00800000/CAP_STAT23 repeats and SSH fails. No readable local console
or successful device-state query. The parameter request is retained in the
receipt; a post-bind sysfs parameter read was impossible after lost SSH.

This negative test shows removing compute queue submissions did not prevent
the failure. It does not isolate the exact following instruction or establish
that no asynchronous work caused it. Do not keep treating compute MQD mapping
as the sole proven cause. Next source instrumentation should distinguish the
post-resource GFX/KIQ tests and subsequent init stages; incoming contributor
patches remain pending actual delivery and review. No further hardware retry
was attempted in this turn.

User observed a green screen during this zero-compute-queue trial; no readable console was reported.
