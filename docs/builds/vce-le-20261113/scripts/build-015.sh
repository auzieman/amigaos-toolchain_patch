#!/bin/bash
# Candidate015 = our verified 014 tree + 0034 (VCE software little-endian messages).
# Run in tabor-build:kernel with /work = tabor-work, /priv = amigaos-toolchain_patch/docs/builds (ro).
set -euo pipefail
B=/work/builds/e2e014; W=/work/builds/e2e015
PATCH=/priv/vce-le-20261113/0034-vce-software-little-endian-messages.patch
[ "$(sha256sum "$B/output/drivers/gpu/drm/amd/amdgpu/amdgpu.ko" | cut -d' ' -f1)" = 099a4e2477910f7c3b870946ae167f90bc9b5b3fbcc4923ad654dad20ad0a6bd ]
rm -rf "$W"; mkdir -p "$W/output"; cp -a "$B/source" "$W/source"
cd "$W/source"; patch -p1 --no-backup-if-mismatch -s < "$PATCH"; echo "applied $(basename "$PATCH") $(sha256sum "$PATCH" | cut -c1-16)"
sed 's/^CONFIG_LOCALVERSION="-tabor-e2e-014"$/CONFIG_LOCALVERSION="-tabor-e2e-015"/' "$B/output/.config" > "$W/output/.config"
M="make -s -C $W/source O=$W/output ARCH=powerpc CROSS_COMPILE=powerpc-linux-gnu-"
$M olddefconfig
diff <(grep -v LOCALVERSION= "$B/output/.config") <(grep -v LOCALVERSION= "$W/output/.config") && echo "config: only LOCALVERSION differs from 014"
$M -j"$(nproc)" vmlinux modules dtbs 2>&1 | grep -E "warning|error" || true
[ "$(cat "$W/output/include/config/kernel.release")" = 6.12.113-tabor-e2e-015 ]
sha256sum "$W/output/drivers/gpu/drm/amd/amdgpu/amdgpu.ko" "$W/output/.config" "$W/output/Module.symvers"
