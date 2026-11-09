#!/bin/sh
set -eu
trap 'r=$?; printf "%s\n" "$r" > /fresh/result.exit' EXIT
# Existing patched source/compiler and baseline sysroot remain read-only.
mkdir -p /fresh/sysroot/usr/include
for name in linux asm asm-generic; do
 cp -a /sysroot/usr/include/$name /fresh/sysroot/usr/include/
done
cd /work/glibc-gcc14-002
make -j4 MAKEINFO=: OBJCOPY=/usr/bin/powerpc-linux-gnu-objcopy STRIP=/usr/bin/powerpc-linux-gnu-strip install_root=/fresh/sysroot install > /fresh/glibc-install.log 2>&1
mkdir /fresh/compiler
cd /fresh/compiler
/work/modern/configure --target=powerpc-linux-gnuspe --prefix=/opt/tabor-gcc14-candidate --with-sysroot=/opt/tabor-gcc14-candidate/sysroot --with-build-sysroot=/fresh/sysroot --enable-languages=c,c++ --disable-bootstrap --disable-multilib --disable-nls --enable-shared --enable-threads=posix --disable-libsanitizer --disable-libquadmath --disable-libgomp --enable-checking=release --with-cpu=8548 --with-long-double-128 --enable-e500-double --with-as=/usr/bin/powerpc-linux-gnu-as --with-ld=/usr/bin/powerpc-linux-gnu-ld > /fresh/configure.log 2>&1
make -j4 AR_FOR_TARGET=/usr/bin/powerpc-linux-gnu-ar RANLIB_FOR_TARGET=/usr/bin/powerpc-linux-gnu-ranlib NM_FOR_TARGET=/usr/bin/powerpc-linux-gnu-nm all-gcc all-target-libgcc all-target-libstdc++-v3 all-target-libatomic > /fresh/build.log 2>&1
make -j4 DESTDIR=/fresh/stage install-gcc install-target-libgcc install-target-libstdc++-v3 install-target-libatomic > /fresh/install.log 2>&1
cp -a /fresh/sysroot /fresh/stage/opt/tabor-gcc14-candidate/sysroot
