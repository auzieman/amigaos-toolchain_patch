#!/bin/sh
# #39: generate patches/qemu/0002 from a clean qemu 11.1.3 tree with 0001 applied.
# Inputs on the replica: /tmp/q39/edit-qemu-0002.py, /tmp/q39/0001.patch. Prints the patch on stdout.
set -e
Q=/srv/data1/tabor-build/work/qemu-user; T=/tmp/q39/gen; rm -rf $T; mkdir -p $T
tar -xJf $Q/qemu-11.1.3.tar.xz -C $T qemu-11.1.3/linux-user qemu-11.1.3/target/ppc
cd $T/qemu-11.1.3 && patch -p1 -s --batch < /tmp/q39/0001.patch >&2 || true
cd $T && cp -a qemu-11.1.3 a && mv qemu-11.1.3 b
python3 /tmp/q39/edit-qemu-0002.py $T/b >&2
cd $T && diff -ruN a/linux-user b/linux-user | sed -e 's|^\(---\|+++\) \([^\t]*\)\t.*|\1 \2|' || true
