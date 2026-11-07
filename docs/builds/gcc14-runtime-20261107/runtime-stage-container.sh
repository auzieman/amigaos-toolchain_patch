#!/bin/sh
set -eu
cd /work/glibc-gcc14-001
make -j4 MAKEINFO=: OBJCOPY=/usr/bin/powerpc-linux-gnu-objcopy STRIP=/usr/bin/powerpc-linux-gnu-strip install_root=/work/runtime-stage-001 install > install-002.log 2>&1
mkdir /work/runtime-probe-001
/work/build-stage1/gcc/xgcc -B/work/build-stage1/gcc/ --sysroot=/sysroot -I/work/runtime-stage-001/usr/include -isystem /sysroot/usr/include -mcpu=8548 -mabi=spe -mspe -mfloat-gprs=double -mlong-double-128 -O2 -fno-pie -no-pie -nostdlib -nostartfiles /work/glibc-gcc14-001/csu/crt1.o /work/glibc-gcc14-001/csu/crti.o /work/build-stage1/gcc/crtbegin.o /probe.c -L/work/glibc-gcc14-001 -L/work/glibc-gcc14-001/math -Wl,-rpath-link=/work/glibc-gcc14-001 -Wl,-dynamic-linker=/lib/ld.so.1 -lm -lc -lgcc /work/build-stage1/gcc/crtend.o /work/glibc-gcc14-001/csu/crtn.o -o /work/runtime-probe-001/spe-abi
