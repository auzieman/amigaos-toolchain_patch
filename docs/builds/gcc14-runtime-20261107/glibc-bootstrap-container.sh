#!/bin/sh
set -eu
mkdir /work/glibc-gcc14-001
cd /work/glibc-gcc14-001
export CC='/work/build-stage1/gcc/xgcc -B/work/build-stage1/gcc/ --sysroot=/sysroot'
export BUILD_CC=gcc CXX=false
export CFLAGS='-O2 -g0 -mcpu=8548 -mabi=spe -mspe -mfloat-gprs=double -mlong-double-128'
export AR=powerpc-linux-gnu-ar RANLIB=powerpc-linux-gnu-ranlib
export AS=powerpc-linux-gnu-as LD=powerpc-linux-gnu-ld NM=powerpc-linux-gnu-nm
export OBJDUMP=powerpc-linux-gnu-objdump READELF=powerpc-linux-gnu-readelf
export OBJCOPY=powerpc-linux-gnu-objcopy STRIP=powerpc-linux-gnu-strip
set +e
/source/configure --build=x86_64-linux-gnu --host=powerpc-linux-gnuspe --prefix=/usr --with-headers=/sysroot/usr/include --disable-werror --disable-nscd --enable-kernel=3.2 > configure.log 2>&1
result=$?
if [ "$result" -eq 0 ]; then make -j4 > build.log 2>&1; result=$?; fi
printf '%s\n' "$result" > result.exit
exit "$result"
