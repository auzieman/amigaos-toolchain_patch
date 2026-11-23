#!/bin/bash
# Kernel 020 = kernel 019 source + 0038 (#48, exec starts with a defined SPEFSCR),
# built with the tabor3 GCC14 SPE SDK (candidate 0001-0024). Config: 017's, LOCALVERSION only.
# Runs inside tabor-gcc14-spe-sdk:local with /k = the k020-spe work dir and the tabor3 SDK
# mounted over /usr/lib/tabor-spe-toolchain.
set -uo pipefail
apt-get update -qq >/dev/null 2>&1; DEBIAN_FRONTEND=noninteractive apt-get install -y -qq bc libssl-dev libelf-dev kmod cpio rsync python3 device-tree-compiler u-boot-tools >/dev/null 2>&1
export PATH=/usr/lib/tabor-spe-toolchain/bin:$PATH
powerpc-linux-gnuspe-gcc --version | head -1
rm -rf /k/out; mkdir -p /k/out
sed 's/^CONFIG_LOCALVERSION="-tabor-e2e-017"$/CONFIG_LOCALVERSION="-tabor-e2e-020"/' /k/output/.config > /k/out/.config
M="make -s -C /k/source O=/k/out ARCH=powerpc CROSS_COMPILE=powerpc-linux-gnuspe-"
$M olddefconfig
grep "^CONFIG_CC_VERSION_TEXT" /k/out/.config
$M -j"$(nproc)" vmlinux modules dtbs uImage > /k/make.log 2>&1; echo "make exit=$?"
grep -E "warning:" /k/make.log | sort | uniq -c | head; grep -E "error:|internal compiler error" /k/make.log | head
cat /k/out/include/config/kernel.release
sha256sum /k/out/vmlinux /k/out/arch/powerpc/boot/uImage /k/out/drivers/gpu/drm/amd/amdgpu/amdgpu.ko /k/out/arch/powerpc/boot/dts/fsl/tabor-a1222.dtb 2>&1
# --- stage tarball: FAT files under boot/, modules under lib/modules (extract at /) ---
REL=$(cat /k/out/include/config/kernel.release); [ "$REL" = 6.12.113-tabor-e2e-020 ] || exit 1
st=/k/stage; rm -rf $st; mkdir -p $st/boot/boot/e2e-020 $st/lib/modules
powerpc-linux-gnuspe-objcopy -O binary /k/out/vmlinux /k/vmlinux.bin
ks=$(stat -c %s /k/vmlinux.bin); [ "$ks" -lt $((0x04000000)) ] || { echo "kernel too large"; exit 1; }
gzip -9 -n -c /k/vmlinux.bin > /k/vmlinux.bin.gz
mkimage -A ppc -O linux -T kernel -C gzip -a 0 -e 0 -n "Linux-$REL" -d /k/vmlinux.bin.gz $st/boot/boot/e2e-020/uImage >/dev/null
us=$(stat -c %s $st/boot/boot/e2e-020/uImage); [ $((0x04000000 + us)) -lt $((0x08000000)) ] || exit 1
cp /k/out/arch/powerpc/boot/dts/fsl/tabor-a1222.dtb $st/boot/boot/e2e-020/tabor.dtb
sed -e "s/@PARTUUID@/a1222013-02/" -e "s/@K@/020/g" -e 's/ panic=-1$/ panic=0/' /k/boot.cmd > $st/boot/boot-020.cmd
mkimage -A ppc -O linux -T script -C none -n "A1222 rescue 020" -d $st/boot/boot-020.cmd $st/boot/boot-020.scr >/dev/null
$M INSTALL_MOD_PATH=$st modules_install
depmod -b $st "$REL"
( cd $st && find . -type f ! -name SHA256SUMS -exec sha256sum {} + | sed 's| \./| /|' > SHA256SUMS )
tar -C $st --owner=0 --group=0 -cf /k/stage-020.tar .
echo "kernel $ks bytes, uImage $us bytes"; sha256sum /k/stage-020.tar
