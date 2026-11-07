#!/bin/sh
set -eu
CANDIDATE=/root/polaris-next/amdgpu-candidate.ko
EXPECTED=403837663941f14ed2b2daf83847786074f3290f01e106f86a86855f2a504732
PCI=/sys/bus/pci/devices/0001:01:00.0
OUT=/root/polaris-next/first-load
[ "$(uname -r)" = 6.12.113-tabor-modular ] || exit 1
if grep -q '^amdgpu ' /proc/modules; then
 echo 'AMDGPU already loaded. Use a fresh boot; refusing warm unload.'
 exit 1
fi
[ -d "$PCI" ] || exit 1
set -- $(/sbin/busybox-modules sha256sum "$CANDIDATE")
[ "$1" = "$EXPECTED" ] || exit 1
[ ! -e "$OUT" ] || { echo 'Log directory exists; preserve it before another test.'; exit 1; }
mkdir "$OUT"
cat /dev/kmsg > "$OUT/kmsg.txt" 2> "$OUT/kmsg.stderr" < /dev/null &
LOGGER=$!
trap 'kill "$LOGGER" 2>/dev/null || true; sync' EXIT
# Resolve installed dependencies without allowing the original driver to probe.
printf '%s\n' tabor-held > "$PCI/driver_override"
trap 'printf "\n" > "$PCI/driver_override"; kill "$LOGGER" 2>/dev/null || true; sync' EXIT
echo "PHASE: dependencies held; loading original without probe"
modprobe amdgpu
echo "PHASE: removing never-bound original"
rmmod amdgpu
echo "PHASE: inserting candidate while PCI held"
insmod "$CANDIDATE"
echo "PHASE: candidate inserted; preparing explicit bind"
printf '\n' > "$PCI/driver_override"
sync
echo "PHASE: binding GPU now"
printf '%s\n' 0001:01:00.0 > /sys/bus/pci/drivers/amdgpu/bind 2> "$OUT/bind.stderr" || true
cat /proc/fb > "$OUT/framebuffers.txt"
cat /proc/modules > "$OUT/modules.txt"
ls -l "$PCI/driver" > "$OUT/binding.txt" 2>&1 || true
sync
echo "Test returned. Evidence: $OUT"
