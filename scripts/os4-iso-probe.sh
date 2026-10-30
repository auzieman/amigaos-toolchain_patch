#!/bin/sh
# Bounded read-only firmware probe, not an A1222 emulator or installation.
set -eu
umask 077
image=$1
iso=$(realpath "$2")
results=$3
test -f "$iso"
test ! -e "$results"
mkdir -p "$results"
results=$(realpath "$results")
docker image inspect "$image" --format '{{.Id}}' > "$results/image-id.txt"
sha256sum "$iso" > "$results/iso.sha256"
docker run --rm --cpus=1 --memory=1g --network none --entrypoint sh \
 -v "$iso:/media/install.iso:ro" -v "$results:/results" "$image" -c '
 qemu-system-ppc --version > /results/version.txt
 timeout 30 qemu-system-ppc -machine sam460ex -m 512 -display none \
  -serial file:/results/serial.log -monitor none -nic none \
  -drive if=none,id=cd,format=raw,readonly=on,file=/media/install.iso \
  -device ide-cd,drive=cd,bus=ide.1 > /results/qemu.log 2>&1
 code=$?
 echo "$code" > /results/exit-status.txt
 case "$code" in 0|124) exit 0;; *) exit "$code";; esac
 '
