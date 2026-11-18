#!/bin/sh
# glibc 0008 test: build one C probe (source on stdin) for the A1222 against the rebuilt glibc, run
# from /opt/gz/lib (its own ld.so, libc, libm; the live bundle is not touched), and pack that
# directory. Usage: build-probe-gz.sh NAME < NAME.c ; writes $W/out/NAME and $W/out/gz-lib.tar
set -e
N=$1; W=/srv/data1/tabor-build/work/glibc-zs; B=$W/source/build-tree/powerpcspe-libc
S=/srv/data1/tabor-build/work/gcc14-pkgsdk-003/out/usr/lib/tabor-spe-toolchain
cat > $W/out/$N.c
mkdir -p $W/out/gz/lib
cp $B/elf/ld.so $W/out/gz/lib/ld.so.1; cp $B/libc.so $W/out/gz/lib/libc.so.6; cp $B/math/libm.so $W/out/gz/lib/libm.so.6
docker run --rm -v $S:/usr/lib/tabor-spe-toolchain:ro -v $W/out:/out --entrypoint bash tabor-local/mesa-spe -c \
 "/usr/lib/tabor-spe-toolchain/bin/powerpc-linux-gnuspe-gcc -O2 -o /out/$N /out/$N.c -lm -Wl,--disable-new-dtags -Wl,--dynamic-linker=/opt/gz/lib/ld.so.1 -Wl,-rpath=/opt/gz/lib" >&2
cd $W/out && tar -cf gz-lib.tar -C gz lib && sha256sum gz/lib/* $N >&2
