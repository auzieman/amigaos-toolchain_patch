#!/bin/bash
# Candidate016 = our 015 tree + 0035 (compute user IBs fetched LE under polaris11_le_user_ib).
# Run in tabor-build:kernel with /work = tabor-work, /priv = amigaos-toolchain_patch/docs/builds (ro).
set -euo pipefail
B=/work/builds/e2e015; W=/work/builds/e2e016
PATCH=/priv/compute-le-20261114/0035-amdgpu_cs-hunk.patch
[ "$(sha256sum "$B/output/drivers/gpu/drm/amd/amdgpu/amdgpu.ko" | cut -d' ' -f1)" = 8b6cb5825e9e644cdbc501d704bfe9762bdf622550951f0a375719e7acf962f0 ]
rm -rf "$W"; mkdir -p "$W/output"; cp -a "$B/source" "$W/source"
cd "$W/source"; patch -p1 --no-backup-if-mismatch -s < "$PATCH"; echo "applied $(basename "$PATCH") $(sha256sum "$PATCH" | cut -c1-16)"
sed 's/^CONFIG_LOCALVERSION="-tabor-e2e-015"$/CONFIG_LOCALVERSION="-tabor-e2e-016"/' "$B/output/.config" > "$W/output/.config"
M="make -s -C $W/source O=$W/output ARCH=powerpc CROSS_COMPILE=powerpc-linux-gnu-"
$M olddefconfig
diff <(grep -v LOCALVERSION= "$B/output/.config") <(grep -v LOCALVERSION= "$W/output/.config") && echo "config: only LOCALVERSION differs from 015"
$M -j"$(nproc)" vmlinux modules dtbs 2>&1 | grep -E "warning|error" || true
[ "$(cat "$W/output/include/config/kernel.release")" = 6.12.113-tabor-e2e-016 ]
sha256sum "$W/output/drivers/gpu/drm/amd/amdgpu/amdgpu.ko" "$W/output/.config" "$W/output/Module.symvers"
