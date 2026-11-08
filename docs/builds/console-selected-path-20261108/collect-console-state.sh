#!/bin/sh
# Run over existing SSH only after a fresh, successful normal modprobe returns.
# Cached state only: no rebinding, forced detection, register reads, or painting.
set -eu
expected=6.12.113-tabor-e2e-007
actual=$(uname -r)
printf 'KERNEL=%s\n' "$actual"
if [ "$actual" != "$expected" ]; then
 printf 'REFUSED: expected %s\n' "$expected" >&2
 exit 2
fi
printf '\nBOOT ARGUMENTS\n'
cat /proc/cmdline
printf '\nFRAMEBUFFERS\n'
cat /proc/fb
for fb in /sys/class/graphics/fb*; do
 [ -d "$fb" ] || continue
 printf '\n%s\n' "$fb"
 for item in name virtual_size bits_per_pixel stride blank; do
  [ -f "$fb/$item" ] || continue
  printf '%s=' "$item"
  cat "$fb/$item"
 done
done
printf '\nVT CONSOLE BINDINGS\n'
for vt in /sys/class/vtconsole/vtcon*; do
 [ -d "$vt" ] || continue
 printf '%s ' "$vt"
 cat "$vt/name" "$vt/bind"
done
printf '\nCACHED CONNECTOR STATE\n'
for connector in /sys/class/drm/card*-*; do
 [ -f "$connector/status" ] || continue
 printf '\n%s\n' "$connector"
 cat "$connector/status"
 [ ! -f "$connector/enabled" ] || cat "$connector/enabled"
 [ ! -f "$connector/modes" ] || cat "$connector/modes"
done
printf '\nDRM DEVICE NODES\n'
ls -l /dev/dri /dev/fb* 2>/dev/null || :
printf '\n2D_ACCEPTANCE=PENDING_VISUAL\n'
# A registered framebuffer and connected connector do not prove visible output.
