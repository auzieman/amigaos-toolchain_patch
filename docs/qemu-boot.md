# Edge e500v2 boot smoke test

This lane uses stock QEMU's generic ppce500 machine, e500v2 CPU, TCG,
two cores, 512 MiB RAM and serial output. No GPU passthrough, desktop,
network listener, disk image or physical boot media is required.
Reference: https://www.qemu.org/docs/master/system/ppc/ppce500.html .

The full Debian 6.12.113-1 Tabor build completed in BKC run
b57b3f7b-cc3c-43b4-95a7-31b11186478b. Its configuration disables
CONFIG_PPC_QEMU_E500, so it is preserved as a separate compile result.
The emulator lane re-extracts the same pinned Debian archives, reapplies the
same Tabor patch, and uses profiles/qemu/e500v2-smoke.config through
scripts/debian-iterate.py --kernel-profile qemu-smoke. This minimal config
builds vmlinux and the scoped Tabor object/DTB, not the full module set.
It retains CONFIG_TABOR and CONFIG_SPE alongside the QEMU platform.
QEMU supplies its own generated device tree; do not pass the real Tabor DTB.

scripts/qemu-boot-smoke.py builds boot/init-smoke.S with the recorded PowerPC
assembler/linker into a static PPC32 ELF /init and packs a newc initramfs.
It runs the guest without networking for at most 60 seconds, retains the
serial log, exact invocation, QEMU version, image identity and input hashes,
and accepts only the init marker without a kernel panic. PID1 then waits;
the harness terminates this disposable VM at the time limit.
This init has no shell, libc or floating-point operations. It tests kernel
entry into userspace only. SPE arithmetic/ABI, glibc, headless Mesa and real
A1222 firmware/board boot remain separate acceptance gates.

Run inside the retained QEMU tools image, with absolute container paths:

```sh
python3 /project/scripts/qemu-boot-smoke.py \
  --kernel /work/linux-001/output/vmlinux \
  --init-source /project/boot/init-smoke.S \
  --output /results/boot-001 --image-id sha256:IMAGE_ID
```

Use a fresh output directory for every attempt. Keep project/kernel mounts
read-only for the actual boot container; bound it to two host CPUs and 2 GiB
RAM with Docker networking disabled. The CPU architecture is emulated by TCG.
docker/Dockerfile.qemu documents the equivalent tools-image extension.
The actual initial image was retained with docker commit after package installation;
its identity and package inventory are recorded.
The QEMU tools image extends the retained Debian build image by installing
qemu-system-ppc; installation log, package inventory and resulting image ID
must accompany the boot receipt. This records the actual environment rather
than claiming a snapshot-reproducible apt rebuild.

Initial config checks required explicit FSL_SOC_BOOKE and DEBUG_KERNEL
dependencies before their child selections could survive allnoconfig. The
failed checks were retained before fresh extractions. dpkg-source also
leaves an orig archive beside its extracted source; duplicate copies from
the failed attempts were SHA256-compared with the canonical cache before
removal to recover local workspace headroom. Cached originals remain.

The first linked emulator profile (attempt-004) produced no serial kernel text
within 60 seconds. The minimal config lacked PHYS_64BIT (QEMU's CCSR is at
0xFE0000000) and SERIAL_OF_PLATFORM. Both are now explicit in the seed.
Source reference: https://github.com/qemu/qemu/blob/v10.0.0/hw/ppc/e500plat.c .
The retry is attempt-005; each attempt has independent logs/receipts.
The harness writes serial.log live, rather than buffering output until exit.

For local monitoring, scripts/edge-dashboard.py labels host-wide CPU/RAM and
per-container metrics separately from uninstrumented guest CPU usage. The first
CLI init does not mount procfs or provide a guest monitor. Two screenshot-ready
Terminology windows were placed on desktop 4 (E desk 3,0), external monitor:
one tails /var/lib/bkc/tabor-qemu/live.log, the other runs the ANSI dashboard
through SSH. No VNC listener or desktop service was enabled on edge.

## Verified result — 2026-10-30

Attempt-005 passed the 60-second test with QEMU 10.0.13: Linux 6.12.113
identified QEMU ppce500/e500v2, brought up two CPUs, unpacked the initramfs
and printed TABOR_QEMU_INIT_OK after executing /init. No kernel panic was
observed. The VM was terminated by the bounded harness, not left running.
The two desktop terminals remain open with retained output/dashboard.

[Structured build/boot evidence](builds/20261030-qemu-boot.json) records the
exact image identity, commands and artifact hashes; [serial transcript](builds/20261030-qemu-serial.log)
retains the actual console output. Collected results passed SHA256SUMS and
boot kernel hash matches the kernel build receipt. Source-init and config-seed
hashes match the repository inputs. Generated source/object trees were
discarded only after evidence retention.

This validates a separate minimal QEMU config of the patched Debian source,
not the full Tabor artifact against real board firmware. Kernel timestamp
1970-01-01 is the runner's intentional fixed build timestamp, not the test date.
No modern glibc, SPE arithmetic, guest CPU monitor, SDL/GL, AMD graphics or
physical A1222 boot result is claimed. The init deliberately has no shell;
an interactive rescue rootfs is a subsequent deliverable.
