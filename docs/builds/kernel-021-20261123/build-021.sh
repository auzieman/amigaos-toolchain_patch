#!/bin/bash
# Kernel 021 = e2e-usb-20261113-016 source + 0037 (Derf, #35) + 0038 (Derf, #48/#41)
# + 0039 (trace prints to debug). Config: 016's plus the changes below. Same tools
# image and compiler as 016 (Debian powerpc-linux-gnu-gcc 14.2.0), so only these
# changes differ. Runs in tools image sha256:2781e118... with /k = the work dir.
set -euo pipefail
cd /k
S=/k/source O=/k/out
M="make -s -C $S O=$O ARCH=powerpc CROSS_COMPILE=powerpc-linux-gnu-"
mkdir -p $O; cp /k/config-016 $O/.config
C="$S/scripts/config --file $O/.config"
$C --set-str LOCALVERSION -tabor-e2e-021
$C --set-val NR_CPUS 2
$C --disable PREEMPT_NONE --enable PREEMPT_VOLUNTARY
$C --disable HZ_250 --enable HZ_1000 --set-val HZ 1000
$C --enable DYNAMIC_DEBUG
$C --module SND_HDA_INTEL --module SND_HDA_CODEC_HDMI
$M olddefconfig
for o in LOCALVERSION NR_CPUS PREEMPT_VOLUNTARY PREEMPT_NONE HZ DYNAMIC_DEBUG SND_HDA_INTEL SND_HDA_CODEC_HDMI SPE TABOR DRM_AMDGPU; do grep -E "^(# )?CONFIG_$o[= ]" $O/.config; done
$M -j"${JOBS:-4}" vmlinux modules dtbs > /k/make.log 2>&1 || { tail -30 /k/make.log; exit 1; }
grep -E "warning:" /k/make.log | sort | uniq -c | head
REL=$(cat $O/include/config/kernel.release); [ "$REL" = 6.12.113-tabor-e2e-021 ]
st=/k/stage; rm -rf $st; mkdir -p $st/fat/boot/e2e-021 $st/root
powerpc-linux-gnu-objcopy -O binary $O/vmlinux /k/vmlinux.bin
ks=$(stat -c %s /k/vmlinux.bin); [ "$ks" -lt $((0x04000000)) ]
gzip -9 -n -c /k/vmlinux.bin > /k/vmlinux.bin.gz
mkimage -A ppc -O linux -T kernel -C gzip -a 0 -e 0 -n "Linux-$REL" -d /k/vmlinux.bin.gz $st/fat/boot/e2e-021/uImage >/dev/null
us=$(stat -c %s $st/fat/boot/e2e-021/uImage); [ $((0x04000000 + us)) -lt $((0x08000000)) ]
cp $O/arch/powerpc/boot/dts/fsl/tabor-a1222.dtb $st/fat/boot/e2e-021/tabor.dtb
$M INSTALL_MOD_PATH=$st/root modules_install
depmod -b $st/root -F $O/System.map "$REL"
rm -f $st/root/lib/modules/$REL/build $st/root/lib/modules/$REL/source
( cd $st && find . -type f -exec sha256sum {} + | sort -k2 > /k/SHA256SUMS )
tar -C $st --owner=0 --group=0 -cf /k/stage-021.tar fat root
echo "kernel $ks bytes, uImage $us bytes, modules $(find $st/root -name '*.ko' | wc -l)"
sha256sum $O/vmlinux $st/fat/boot/e2e-021/uImage $st/fat/boot/e2e-021/tabor.dtb /k/stage-021.tar
