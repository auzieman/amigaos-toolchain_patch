#!/bin/sh
# #39: apply patches/qemu 0001 then 0002 (copied to /tmp/q39/s-*) to a clean qemu 11.1.3 tarball
# the way scripts/build-qemu-ppc.py does, and compare the result with the tested replica tree.
set -e
T=/tmp/q39/series; rm -rf $T; mkdir -p $T; tar -xJf /srv/data1/tabor-build/work/qemu-user/qemu-11.1.3.tar.xz -C $T
cd $T/qemu-11.1.3
for p in /tmp/q39/s-0001-*.patch /tmp/q39/s-0002-*.patch; do patch -p1 --batch --forward --no-backup-if-mismatch < $p > /dev/null && echo "applied $(basename $p)"; done
for f in linux-user/main.c linux-user/qemu.h linux-user/syscall.c linux-user/ppc/target_prctl.h target/ppc/cpu.c; do cmp -s $f /srv/data1/tabor-build/work/qemu-user/src/$f && echo "same as tested: $f" || echo "DIFFERS: $f"; done
