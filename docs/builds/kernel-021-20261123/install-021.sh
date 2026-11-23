#!/bin/sh
# Install kernel 021 on the A1222 (run on the board as root, from the stage dir).
# Adds files only: /boot/e2e-021 on the SanDisk FAT, the 021 module tree, the
# root marker, and the order-independent boot.scr on both sticks. The existing
# 016 kernel, DTB and modules stay. Old scripts are kept as *.pre-021.
# Rollback: copy boot.scr.pre-021 back to boot.scr on the SanDisk FAT (and
# delete boot.scr on the PNY FAT), or at the U-Boot prompt:
#   fatload usb 0:1 0x09000000 /boot-016.scr; source 0x09000000   (try usb 1:1 too)
set -eu
STAGE=${1:-.}; REL=6.12.113-tabor-e2e-021
cd "$STAGE"; sha256sum -c --quiet SHA256SUMS.board
SD=/dev/disk/by-partuuid/a1221115-01; PNY=/dev/disk/by-partuuid/7e79cdbd-01
[ "$(blkid -o value -s TYPE $SD)" = vfat ]; [ "$(blkid -o value -s TYPE $PNY)" = vfat ]
# modules into the running root (new release dir only)
[ ! -e /lib/modules/$REL ]; cp -a root/lib/modules/$REL /lib/modules/
# HDMI audio is new in 021: keep it from autoloading until tested by hand.
echo 'blacklist snd_hda_intel' > /etc/modprobe.d/tabor-021-hda-hold.conf
m=/run/tabor-sd; mkdir -p $m; mount $SD $m
for f in boot.cmd boot.scr; do [ -e $m/$f.pre-021 ] || cp -p $m/$f $m/$f.pre-021; done
mkdir -p $m/boot/e2e-021; cp fat/boot/e2e-021/uImage fat/boot/e2e-021/tabor.dtb $m/boot/e2e-021/
cp boot/tabor.id boot/boot.cmd boot/boot.scr boot/boot-016.cmd boot/boot-016.scr $m/
sync; ( cd $m && sha256sum boot/e2e-021/uImage boot/e2e-021/tabor.dtb tabor.id boot.scr boot-016.scr ); umount $m
# PNY: same scripts, no marker, so whichever stick is usb 0 runs the same search.
p=/run/tabor-pny; mkdir -p $p; mount $PNY $p
cp boot/boot.cmd boot/boot.scr boot/boot-016.cmd boot/boot-016.scr $p/; [ ! -e $p/tabor.id ]
sync; ( cd $p && sha256sum boot.scr boot-016.scr ); umount $p
echo "installed $REL; 016 untouched"
