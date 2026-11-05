#!/bin/sh
# Read-only hardware probes. Write results only into a private output directory.
# No raw flash reads, PCI configuration writes, ROM-enable or driver changes.
set -eu
umask 077
out=${1:-/root/a1222-qemu-inventory}
if [ -e "$out" ]; then
 echo 'Refusing existing output; select a new directory' >&2
 exit 1
fi
mkdir -p "$out/pci"
uname -a > "$out/uname.txt"
for name in cpuinfo meminfo cmdline iomem ioports interrupts modules mounts mtd; do
 if [ -r "/proc/$name" ]; then
  cat "/proc/$name" > "$out/$name.txt"
 fi
done
/bin/busybox dmesg > "$out/dmesg.txt"
if [ -r /sys/firmware/fdt ]; then
 cat /sys/firmware/fdt > "$out/live-uboot-fixed.dtb"
fi
for dev in /sys/bus/pci/devices/*; do
 [ -d "$dev" ] || continue
 name=${dev##*/}
 mkdir "$out/pci/$name"
 for field in vendor device subsystem_vendor subsystem_device class revision irq resource modalias uevent; do
  if [ -r "$dev/$field" ]; then
   cat "$dev/$field" > "$out/pci/$name/$field"
  fi
 done
done
ls -l /sys/class/drm > "$out/drm.txt" 2>&1 || true
ls -l /sys/bus/pci/devices/0001:01:00.0/rom > "$out/video-rom-interface.txt" 2>&1 || true
echo 'Private physical-board inventory; not a firmware image or QEMU implementation.' > "$out/README.txt"
echo 'No ROM contents, private SSH keys or credentials were collected.' >> "$out/README.txt"
echo "Inventory ready: $out"
