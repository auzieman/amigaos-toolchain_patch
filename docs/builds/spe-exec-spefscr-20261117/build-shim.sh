#!/bin/sh
# Build one LD_PRELOAD shim (C source on stdin) for the A1222 bundle. Usage: build-shim.sh NAME < NAME.c
set -e
N=$1; W=/srv/data1/tabor-build/work/mesa-spe-work; S=/srv/data1/tabor-build/work/gcc14-pkgsdk-003/out/usr/lib/tabor-spe-toolchain
cat > $W/exp457/$N.c
docker run --rm -v $S:/usr/lib/tabor-spe-toolchain:ro -v $W:/work --entrypoint bash tabor-local/mesa-spe -c \
 "/usr/lib/tabor-spe-toolchain/bin/powerpc-linux-gnuspe-gcc -O2 -fPIC -shared -o /work/exp457/$N.so /work/exp457/$N.c" >&2
cat $W/exp457/$N.so
