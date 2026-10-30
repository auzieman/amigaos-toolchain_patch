# Isolated kernel runner

The first executable profile reproduces the vendor 5.4-rc3 source/config/DTS.
Modern kernel forward ports require their own reviewed pinned profiles/patches.
The baseline runner builds vmlinux, modules and DTBs; board boot wrapping is a
separate milestone. It does not claim a glibc build or bootable A1222 image.

Build the tooling image on the lab builder, supplying an actual reviewed digest:

```sh
docker build --build-arg BASE_IMAGE="$TABOR_BASE_IMAGE" -f docker/Dockerfile.kernel -t tabor-kernel-tools .
```

BASE_IMAGE has no floating default. Apt package versions are recorded in each
receipt; rebuilding this Dockerfile alone does not reproduce those versions.
Retain/pin the resulting tools image digest for accepted builds. A package
snapshot/lock is a later improvement before claiming reproducible image rebuilds.

Stage the board repository at `/inputs` read-only, this project at `/project`
read-only and a fresh output volume at `/work`. In a constrained lab job:

```sh
docker run --rm --cpus=2 --memory=4g --network=none \
  --mount type=bind,src="$TABOR_INPUTS",dst=/inputs,readonly \
  --mount type=bind,src="$TABOR_PROJECT",dst=/project,readonly \
  --mount type=bind,src="$TABOR_OUTPUT",dst=/work \
  "$TABOR_TOOLS_IMAGE" --profile /project/profiles/kernel-vendor-5.4-rc3.json \
  --inputs /inputs --work /work/run-001 --jobs 2 --image-id "$TABOR_TOOLS_IMAGE"
```

Use a digest-identified tools image for acceptance; the runner requires its
sha256 identity and records it. Use `--prepare-only` to verify exact source,
patch/config/DTS inputs and apply patches without compiling. It still creates a
fresh source checkout; budget disk space accordingly. Neither mode fetches
remote source: intake must supply the exact Git revision first. No reset/clean
is performed against the input repository. Logs and a receipt survive failures.

The source archive comes from the recorded Git commit, excluding local changes.
Patches apply in declared order with git apply --check, without fuzz. A failed
run needs a new work directory rather than silently resuming partial state.

Known boundary: a modern distro compiler may expose old vendor-kernel failures;
retain that failure before adjusting sources or selecting a historical compiler.
Do not label it evidence that modern glibc or SPE userspace works.

References: https://docs.kernel.org/kbuild/kbuild.html and
https://docs.docker.com/reference/dockerfile/ .
