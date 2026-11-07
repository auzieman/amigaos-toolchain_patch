#!/bin/sh
# Run on the A1222 rescue root. Explicit candidate, hash and fresh output required.
# Holds PCI matching while loading modules; records the actual failed/successful bind.
set -eu
candidate=${1:?candidate module path required}
expected=${2:?candidate SHA256 required}
out=${3:?fresh absolute output directory required}
[ "$(uname -r)" = '6.12.113-tabor-modular' ]
case "$out" in /root/*) ;; *) echo 'Output must be under /root' >&2; exit 1;; esac
[ ! -e "$out" ]
actual=$(/sbin/busybox-modules sha256sum "$candidate")
[ "${actual%% *}" = "$expected" ]
pci=/sys/bus/pci/devices/0001:01:00.0
[ "$(cat "$pci/vendor")" = '0x1002' ]
[ "$(cat "$pci/device")" = '0x67ff' ]
[ ! -L "$pci/driver" ]
mkdir "$out"
t=/sys/kernel/tracing/instances/a1222-smu-${out##*/}
kpid=
cleanup() {
 if [ -n "$kpid" ]; then kill "$kpid" 2>/dev/null || :; wait "$kpid" 2>/dev/null || :; kpid=; fi
 printf '\n' > "$pci/driver_override"
 if [ -d "$t" ]; then
  echo 0 > "$t/tracing_on"
  for e in amdgpu_device_rreg amdgpu_device_wreg; do
   [ ! -f "$t/events/amdgpu/$e/enable" ] || echo 0 > "$t/events/amdgpu/$e/enable"
  done
 fi
}
trap cleanup EXIT HUP INT TERM
cat /dev/kmsg > "$out/kmsg.txt" 2> "$out/kmsg.stderr" < /dev/null &
kpid=$!
printf '%s\n' a1222-reference-hold > "$pci/driver_override"
if grep -q '^amdgpu ' /proc/modules; then rmmod amdgpu; fi
# Debian-generated dependency metadata resolves prerequisite modules normally.
modprobe amdgpu
rmmod amdgpu
insmod "$candidate"
if [ ! -d /sys/kernel/tracing/events ]; then
 mount -t tracefs tracefs /sys/kernel/tracing
fi
mkdir "$t"
echo 0 > "$t/tracing_on"
echo 4096 > "$t/buffer_size_kb"
filter='did == 26623 && (reg == 428 || reg == 429 || reg == 146 || reg == 148 || reg == 149 || reg == 164)'
for e in amdgpu_device_rreg amdgpu_device_wreg; do
 if [ "$e" = amdgpu_device_rreg ]; then
  printf '%s\n' 'did == 26623 && reg == 149 && value != 0' > "$t/events/amdgpu/$e/filter"
 else
  printf '%s\n' 'did == 26623 && (reg == 429 || reg == 146 || reg == 148 || reg == 149 || reg == 164 || (reg == 428 && (value == 131072 || value == 2147483648 || value == 2147483652)))' > "$t/events/amdgpu/$e/filter"
 fi
 echo 1 > "$t/events/amdgpu/$e/enable"
done
cat /proc/cmdline > "$out/cmdline.txt"
cat "$pci/resource" > "$out/resources.txt"
cat /proc/modules > "$out/modules-before.txt"
echo 1 > "$t/tracing_on"
printf '\n' > "$pci/driver_override"
if printf '%s\n' 0001:01:00.0 > /sys/bus/pci/drivers/amdgpu/bind; then
 echo success > "$out/bind-result.txt"
else
 echo failed > "$out/bind-result.txt"
fi
echo 0 > "$t/tracing_on"
cat "$t/trace" > "$out/registers.trace"
for f in "$t"/per_cpu/cpu*/stats; do
 printf '%s\n' "$f" >> "$out/trace-stats.txt"
 cat "$f" >> "$out/trace-stats.txt"
done
cat /proc/fb > "$out/framebuffers.txt"
dmesg > "$out/dmesg.txt"
cleanup
trap - EXIT HUP INT TERM
sync
echo "Captured PCI resources and SMU register transactions in $out"
