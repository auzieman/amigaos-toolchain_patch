#!/bin/bash
# sparse endian check over amdgpu/radeon/powerplay in the kernel 021 tree (read-only on source).
set -uo pipefail
apt-get update -qq >/dev/null 2>&1; DEBIAN_FRONTEND=noninteractive apt-get install -y -qq sparse bc libssl-dev libelf-dev flex bison >/dev/null 2>&1
sparse --version || true
cd /k; rm -rf sp; mkdir sp; cp out/.config sp/.config
M="make -s -C /k/sparse-src O=/k/sp ARCH=powerpc CROSS_COMPILE=powerpc-linux-gnu-"
$M olddefconfig; $M modules_prepare >/dev/null 2>&1
$M -j8 C=2 CF="-D__CHECK_ENDIAN__ -Wbitwise -Wcast-to-as -fmax-warnings=100000" drivers/gpu/drm/amd/amdgpu/ > /k/sparse-amd-le.log 2>&1
echo "make exit=$?"
grep -cE "warning|error" /k/sparse-amd.log
