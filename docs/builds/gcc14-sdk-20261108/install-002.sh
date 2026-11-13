#!/bin/sh
set -eu
trap 'r=$?; printf "%s\n" "$r" > /fresh/install-002.exit' EXIT
cd /fresh/compiler
make -j4 AR_FOR_TARGET=/usr/bin/powerpc-linux-gnu-ar RANLIB_FOR_TARGET=/usr/bin/powerpc-linux-gnu-ranlib NM_FOR_TARGET=/usr/bin/powerpc-linux-gnu-nm DESTDIR=/fresh/stage-002 install-gcc install-target-libgcc install-target-libstdc++-v3 install-target-libatomic > /fresh/install-002.log 2>&1
cp -a /fresh/sysroot /fresh/stage-002/opt/tabor-gcc14-candidate/sysroot
