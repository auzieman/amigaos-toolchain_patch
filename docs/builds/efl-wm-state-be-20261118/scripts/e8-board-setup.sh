#!/bin/sh
# #8 on the A1222: the e8 chroot in its own tmpfs at /e8 (tarball on stdin), with the board's static
# busybox as /bin and /dev, /proc, /sys bound in. Nothing outside /e8 is written.
set -e
mountpoint -q /e8 || { mkdir -p /e8; mount -t tmpfs -o size=600m,mode=755 tmpfs /e8; }
tar -C /e8 -xf -
cp /bin/busybox /e8/bin/busybox; chroot /e8 /bin/busybox --install -s /bin
for m in dev proc sys; do mountpoint -q /e8/$m || mount --rbind /$m /e8/$m; done
chroot /e8 /bin/sh -c 'dbus-uuidgen --ensure 2>/dev/null; ls /usr/bin | wc -l; Xvfb -version 2>&1 | head -2'
df -h /e8 | tail -1
