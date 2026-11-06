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

## Modular physical graphics candidate

`debian-iterate.py --kernel-profile tabor-modular --mode build` uses
`profiles/images/tabor-modular-kernel.config`. It keeps physical USB/ext4,
networking and keyboard boot support built in, and selects DRM, AMDGPU and
Radeon as modules. Its release suffix is `-tabor-modular`; modules must be
installed beneath that exact kernel release with dependency metadata. Preserve
the known working kernel and module tree. This candidate retains legacy DCE
(`DRM_AMD_DC=n`); it does not claim to repair Polaris SMU startup or support
every alternative GPU. SI/CIK AMDGPU support is compiled as an option, without
forcing driver ownership over Radeon at boot.

Do not deploy only vmlinux/uImage: stage the matching modules, firmware and
module-loading tools together, run depmod for the exact release, and verify
boot-critical built-ins before switching. Initial graphics loading should be
explicit over SSH for diagnosis. Kernel build, module load, KMS/console and
accelerated userspace remain separate checks.

2026-11-05 R730 candidate: `work/tabor-modular-20261105-003`, container
`tabor-modular-build-003`, pinned tools image
`sha256:2781e11839beffa351f8c411d71b7e2bd1ae0336d24c60b407778c3350dd9da0`,
4 CPUs/6GiB/network disabled, cached Linux6.12.113-1 with both board patches.
Build launched; no compile or hardware acceptance recorded yet. Attempts001
and002 failed input preflight (wrong cache mount, then patch filename); neither
produced accepted artifacts. Current physical USB is unchanged.
