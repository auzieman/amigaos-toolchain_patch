# Reconnect and laptop budget — 2026-11-01

The R730 rebooted; cached sources, package artifacts and accepted images remain.
No QEMU guests or build containers were running at reconnect. Restarted the same
hash-verified qemu-live007 kernel / deb-initramfs004 into a fresh software-e008
run directory. Guest native dpkg audit is clean, MemTotal8248388KiB and CPUs0–1
are online. Started E in the guest without starting any local VM/build. RAM-root
user configuration is volatile: first-run wizard state returns after shutdown.
Rendering issue8 and physical/GL acceptance have not changed.

Laptop snapshot: ~11.4GiB total RAM, ~3.2GiB available, no swap. The local viewer
proxy was38MiB/1thread, not evidence of the historical editor crash cause. Other
editor/browser/music processes occupied larger individual RSS snapshots. Do not
sum shared RSS as exact total application memory or infer a crash cause from one
snapshot. No user apps or swap/audio/desktop services were modified. Closed only
three identified stale task-owned SSH forwards for retired test guests.

Moved websockify/noVNC to the R730. Host packages novnc/websockify and dependencies
were installed there, not in the SPE guest or on the laptop. The transient
`tabor-e-novnc.service` runs as owner with192MiB MemoryMax,50% CPU quota,
TasksMax16 and OPENBLAS_NUM_THREADS=1 / OMP_NUM_THREADS=1. Observed one task and
~23MiB memory. Server listens only on127.0.0.1:6089 and proxies127.0.0.1:5921.
Local6089 forwards to server6089 over SSH; local12236 forwards guest SSH22136.
The former laptop Python proxy is stopped. Existing browser was refreshed; no
extra windows were opened. The service is transient and is not boot-enabled.

Remote startup (after checking that this task-owned unit is absent/inactive):

```sh
systemd-run --unit=tabor-e-novnc --property=User=owner \
  --property=MemoryMax=192M --property=CPUQuota=50% --property=TasksMax=16 \
  --property=Restart=on-failure --setenv=OPENBLAS_NUM_THREADS=1 \
  --setenv=OMP_NUM_THREADS=1 /usr/bin/websockify --web=/usr/share/novnc \
  127.0.0.1:6089 127.0.0.1:5921
```

AGENTS.md records the ongoing resource policy: heavy work stays on the builder;
one bounded remote build by default (normally4 CPUs/6GiB), short local commands,
bounded output/server-side log summaries, one existing viewer, explicit thread
limits for unavoidable local numerical/media work. Check laptop headroom at
substantial job starts and after symptoms, without adding an always-on monitor.
Evidence: builds/r730-reconnect-20261101. This is reconnection/infrastructure
verification, not another compiler/graphics acceptance result.
