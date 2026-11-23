#!/bin/sh
# glibc 0008 (e500v2 float zero sign): copy the glibc-002 Debian build (patches 0001-0007), apply
# 0008, and rebuild incrementally in the image that built it, mounted at its original path.
# Output: the rebuilt libm.so.6 and libc.so.6 under $W/out. Usage: build-glibc-zs.sh <0008.patch>
set -e
P=$1; R=/srv/data1/tabor-build/results/glibc-002; W=/srv/data1/tabor-build/work/glibc-zs
mkdir -p $W/out
[ -d $W/source ] || cp -a $R/source $W/source
cp $P $W/0008.patch
cd $W/source
if git apply --check $W/0008.patch 2>/dev/null; then git apply $W/0008.patch; echo "0008 applied"; else
   git apply --check -R $W/0008.patch && echo "0008 already applied"; fi
U=/srv/data1/tabor-build/results/uapi-all-001/linux-libc-dev_6.12.113-1_all.deb
# The kernel headers glibc-002 built with (glibc-002-uapi-install.log): linux-libc-dev 6.12.113.
docker run --rm -v $W/source:/results/glibc-002/source -v $W/out:/out -v $U:/uapi.deb:ro --entrypoint bash tabor-local/glibc-pkg -c '
set -e; dpkg -i --force-downgrade /uapi.deb > /out/uapi.log 2>&1
cd /results/glibc-002/source/build-tree/powerpcspe-libc
command -v powerpc-linux-gnuspe-gcc; date -u +%T
make -j12 > /out/make.log 2>&1 || { tail -30 /out/make.log; exit 1; }
date -u +%T; grep -c "s_fmaf\|s_ldexpf" /out/make.log || true
cp math/libm.so /out/libm.so.6; cp libc.so /out/libc.so.6; sha256sum /out/libm.so.6 /out/libc.so.6'
