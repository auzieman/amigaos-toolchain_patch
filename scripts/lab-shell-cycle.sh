#!/bin/sh
# Stage project + pinned caches first. Each new cycle needs new work/tools/sysroot.
set -eu
umask 077
stage=$1
image=$2
phase=$3
mkdir -p "$stage/work" "$stage/tools" "$stage/sysroot" "$stage/results"
run() {
 docker run --rm --cpus=2 --memory=4g --network=none --entrypoint python3 \
  -v "$stage/project:/project:ro" -v "$stage/toolchain-cache:/cache:ro" \
  -v "$stage/debian-cache:/debian-cache:ro" -v "$stage/work:/work" \
  -v "$stage/tools:/tools" -v "$stage/sysroot:/sysroot" -v "$stage/kernel:/kernel:ro" \
  "$image" "$@"
}
case "$phase" in
 compiler) run /project/scripts/bootstrap-spe-compiler.py --project /project --cache /cache --work /work/gcc-001 --prefix /tools/reference-001 --image-id "$image" ;;
 headers) run /project/scripts/export-linux-headers.py --project /project --cache /debian-cache --work /work/headers-001 --sysroot /sysroot ;;
 libgcc) run /project/scripts/spe-runtime-stage.py --phase libgcc --image-id "$image" ;;
 prepare-libc) run /project/scripts/debian-iterate.py --project /project --cache /debian-cache --component glibc --work /work/glibc-002 --mode prepare --image-id "$image" ;;
 libc) run /project/scripts/spe-runtime-stage.py --phase glibc --image-id "$image" ;;
 shell) run /project/scripts/build-skinny-shell.py --project /project --cache /cache --work /work/shell-001 --tools /tools/reference-001 --sysroot /sysroot --image-id "$image" ;;
 boot) run /project/scripts/qemu-shell-smoke.py --kernel /kernel/vmlinux --initramfs /work/shell-001/shell.cpio --output /work/shell-boot-001 --image-id "$image" ;;
 *) echo 'Unknown stage' >&2;exit 2 ;;
esac
