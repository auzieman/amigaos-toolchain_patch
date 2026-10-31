#!/bin/sh
# Explicit lab-host preparation; does not configure disks, bridges or PCI binding.
set -eu
[ "$(id -u)" = 0 ] || { echo 'Run as root'; exit 1; }
build_user=${1:?Usage: prepare-debian-build-host.sh USER WORKSPACE}
workspace=${2:?Provide an existing-filesystem workspace path}
. /etc/os-release
[ "$ID" = debian ] && [ "$VERSION_ID" = 13 ] || exit 1
id "$build_user" >/dev/null
case "$workspace" in /srv/data[123]/tabor-build) ;; *) echo 'Unexpected workspace'; exit 1;; esac
mountpoint "$(dirname "$workspace")" >/dev/null
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends \
 qemu-system-x86 qemu-system-ppc qemu-user qemu-utils \
 libvirt-daemon-system libvirt-clients virtinst ovmf swtpm docker.io docker-cli \
 rsync git curl ca-certificates build-essential ninja-build meson pkg-config \
 libglib2.0-dev libpixman-1-dev libfdt-dev zlib1g-dev bison flex bc \
 libssl-dev libelf-dev libncurses-dev cpio xz-utils bzip2 file jq pciutils \
 smartmontools device-tree-compiler u-boot-tools binutils-powerpc-linux-gnu \
 gcc-powerpc-linux-gnu python3-venv python3-yaml
usermod -aG kvm,libvirt "$build_user"
# Docker remains root-managed: docker-group membership grants root privileges.
install -d -o "$build_user" -g "$(id -gn "$build_user")" -m 0750 \
 "$workspace" "$workspace/cache" "$workspace/work" "$workspace/results"
systemctl enable --now libvirtd.service docker.service
printf '\nHost preparation complete; reconnect for group membership.\n'
qemu-system-x86_64 --version | head -1
qemu-system-ppc --version | head -1
docker --version
