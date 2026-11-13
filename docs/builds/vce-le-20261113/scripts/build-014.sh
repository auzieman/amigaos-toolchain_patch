#!/bin/bash
# Rebuild upstream candidate014 (6.12.113-tabor-e2e-014) from our verified 007 tree plus the
# private repo's patches 0028-0033 and 014's trace patch, checking every hash in 014's receipt.
# Run in tabor-build:kernel with /work = tabor-work volume, /priv = amigaos-toolchain_patch/docs/builds (ro).
set -euo pipefail
P=/priv; S7=/work/builds/e2e007; W=/work/builds/e2e014
R14=$P/mesa-native-vertex-20261109/kernel014/build-014-receipt.json
PATCHES="gfx-ib-flow-20261108/0028-gfx8-decode-ib-test-writeback-and-record-completion.patch:gfx-ib-flow-20261108/build-receipt.json
ib-fetch-contract-20261108/0029-gfx8-test-explicit-little-endian-ib-fetch.patch:ib-fetch-contract-20261108/build-009-receipt.json
ib-fetch-contract-20261108/0030-gfx8-cpu-envelope-snapshot.patch:ib-fetch-contract-20261108/build-010-receipt.json
predicate-contract-20261109/0031-ring-initialize-predicate-through-encoder.patch:predicate-contract-20261109/build-011-receipt.json
vm-pte-contract-20261109/0032-vm-sdma-serialize-copied-pte-array.patch:vm-pte-contract-20261109/build-012-receipt.json
user-ib-fetch-20261109/0033-polaris-user-ib-explicit-le-diagnostic.patch:user-ib-fetch-20261109/build-013-receipt.json
mesa-native-vertex-20261109/0013-opt-in-prepublish-envelope-trace.patch:mesa-native-vertex-20261109/kernel014/build-014-receipt.json"
jq() { python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print(eval(sys.argv[2]))" "$@"; }

[ "$(sha256sum "$S7/output/.config" | cut -d' ' -f1)" = 78024e6fdcab02d5b5c0922551f41feff2c5cbda9bb5444095b23f5e4358b380 ]
rm -rf "$W"; mkdir -p "$W/output"
cp -a "$S7/source" "$W/source"
cd "$W/source"
for e in $PATCHES; do
  p=${e%%:*}; r=${e##*:}
  [ "$(sha256sum "$P/$p" | cut -d' ' -f1)" = "$(jq "$P/$r" "d['boundary_patch']['patch_sha256']")" ]
  # each boundary's recorded inputs must match before, outputs after
  python3 - "$P/$r" in <<'EOF'
import json,sys,hashlib;b=json.load(open(sys.argv[1]))['boundary_patch']
for f,h in b['inputs'].items(): assert hashlib.sha256(open(f,'rb').read()).hexdigest()==h, f'input {f}'
EOF
  patch -p1 --no-backup-if-mismatch -s < "$P/$p"
  python3 - "$P/$r" <<'EOF'
import json,sys,hashlib;b=json.load(open(sys.argv[1]))['boundary_patch']
for f,h in b['outputs'].items(): assert hashlib.sha256(open(f,'rb').read()).hexdigest()==h, f'output {f}'
EOF
  echo "applied $(basename "$p")"
done
# the full chain of file hashes recorded at 014 (014's own amdgpu_ib.c output overrides 013's)
python3 - "$R14" <<'EOF'
import json,sys,hashlib;d=json.load(open(sys.argv[1]))
want=dict(d['source_patch_chain']['source_files_sha256']); want.update(d['boundary_patch']['outputs'])
for f,h in want.items(): assert hashlib.sha256(open(f,'rb').read()).hexdigest()==h, f'chain {f}'
print(f'source: {len(want)} recorded file hashes match 014')
EOF

sed 's/^CONFIG_LOCALVERSION="-tabor-e2e-007"$/CONFIG_LOCALVERSION="-tabor-e2e-014"/' "$S7/output/.config" > "$W/output/.config"
M="make -s -C $W/source O=$W/output ARCH=powerpc CROSS_COMPILE=powerpc-linux-gnu-"
$M olddefconfig
[ "$(sha256sum "$W/output/.config" | cut -d' ' -f1)" = "$(jq "$R14" "d['config_sha256']")" ] || { echo "config differs from 014"; exit 1; }
echo "config matches 014"
$M -j"$(nproc)" vmlinux modules dtbs 2>&1 | grep -E "warning|error" || true
[ "$(cat "$W/output/include/config/kernel.release")" = 6.12.113-tabor-e2e-014 ]
ko=$(find "$W/output/drivers/gpu/drm/amd/amdgpu" -name amdgpu.ko)
got=$(sha256sum "$ko" | cut -d' ' -f1); want=$(jq "$R14" "d['module_verification']['module_sha256']")
echo "amdgpu.ko $got (014 receipt $want)"; [ "$got" = "$want" ] && echo "amdgpu.ko matches 014" || echo "amdgpu.ko DIFFERS from 014"
sha256sum "$W/output/Module.symvers"
