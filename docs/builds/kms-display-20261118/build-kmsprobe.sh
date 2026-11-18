#!/bin/sh
# Build one KMS/GBM/EGL probe (C source on stdin) with the tabor3 SPE toolchain against the
# mesa-spe4 a1222-gl-spe3 stage. Usage: build-glprobe.sh NAME < NAME.c ; binary on stdout.
set -e
N=$1; W=/srv/data1/tabor-build/work/mesa-spe-work; S=/srv/data1/tabor-build/work/gcc14-pkgsdk-003/out/usr/lib/tabor-spe-toolchain
cat > $W/exp457/$N.c
docker run --rm -v $S:/usr/lib/tabor-spe-toolchain:ro -v $W:/work --entrypoint bash tabor-local/mesa-spe -c \
 "export PATH=/usr/lib/tabor-spe-toolchain/bin:\$PATH; B=/work/mesa-spe4/stage/opt/a1222-gl-spe3; powerpc-linux-gnuspe-gcc -O2 -Wall -I\$B/include -I\$B/include/libdrm -o /work/exp457/$N /work/exp457/$N.c -Wl,--disable-new-dtags -Wl,--dynamic-linker=/opt/a1222-gl-spe3/lib/ld.so.1 -Wl,-rpath=/opt/a1222-gl-spe3/lib -L\$B/lib -Wl,-rpath-link,\$B/lib -lEGL -lGLESv2 -lgbm -ldrm -lm" >&2
cat $W/exp457/$N
