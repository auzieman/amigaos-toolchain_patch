#!/bin/sh
set -eu
umask 077
stage=$1
mkdir -p "$stage/results" "$stage/work"
# Many tiny source files made shared-NFS extraction impractically slow.
# Use local ephemeral work with a minimum free-space check in the runner.
docker pull debian:trixie-slim > "$stage/results/base-pull.log" 2>&1
base=$(docker image inspect debian:trixie-slim --format '{{index .RepoDigests 0}}')
printf '%s\n' "$base" > "$stage/results/base-image.txt"
docker build --build-arg BASE_IMAGE="$base" -f "$stage/project/docker/Dockerfile.kernel" -t tabor-debian-tools:"$(basename "$stage")" "$stage/project" > "$stage/results/tooling-build.log" 2>&1
image=$(docker image inspect tabor-debian-tools:"$(basename "$stage")" --format '{{.Id}}')
printf '%s\n' "$image" > "$stage/results/tools-image.txt"
status=0
for component in linux glibc; do
 if docker run --rm --cpus=2 --memory=4g --network=none --entrypoint python3 \
  -v "$stage/project:/project:ro" -v "$stage/cache:/cache:ro" -v "$stage/work:/work" \
  "$image" /opt/tabor/debian-iterate.py --project /project --cache /cache \
  --component "$component" --work "/work/$component-001" --mode build --jobs 2 --image-id "$image" \
  > "$stage/results/$component-console.log" 2>&1; then
  printf '%s\n' success > "$stage/results/$component-status.txt"
 else
  printf '%s\n' failed > "$stage/results/$component-status.txt"
  status=1
 fi
 if [ -d "$stage/work/$component-001" ]; then
  for file in build.log receipt.json; do
   if [ -f "$stage/work/$component-001/$file" ]; then
    cp "$stage/work/$component-001/$file" "$stage/results/$component-$file"
   fi
  done
 fi
done
if [ -f "$stage/work/linux-001/output/vmlinux" ]; then
 cp "$stage/work/linux-001/output/vmlinux" "$stage/results/vmlinux"
 cp "$stage/work/linux-001/output/.config" "$stage/results/kernel.config"
fi
if [ -f "$stage/work/linux-001/output/arch/powerpc/boot/dts/fsl/tabor-a1222.dtb" ]; then
 cp "$stage/work/linux-001/output/arch/powerpc/boot/dts/fsl/tabor-a1222.dtb" "$stage/results/"
fi
cd "$stage/results"
sha256sum ./* > SHA256SUMS
exit "$status"
