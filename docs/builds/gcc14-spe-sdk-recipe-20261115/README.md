# Portable GCC14 SPE SDK recipe (#33) — 2026-11-15

## Problem

`docs/builds/gcc14-sdk-20261108/build.sh` passes `AR_FOR_TARGET`/`RANLIB_FOR_TARGET`/`NM_FOR_TARGET` to `make all-*` but not to `make install-*`. Re-run in a Debian trixie image that has only `binutils-powerpc-linux-gnu`, the install fails:

```
powerpc-linux-gnuspe-ranlib .../libgcc_eh.a
/bin/bash: line 1: powerpc-linux-gnuspe-ranlib: command not found
make[1]: *** [Makefile:1174: install-shared] Error 127
```

The build server's tools image supplies `powerpc-linux-gnuspe-*` binutils, but the recipe never says so. The launch and build scripts under `docs/builds` are historical receipts with lab paths, so they stay unchanged.

## Change

- `scripts/build-gcc14-spe-sdk.sh` is a portable recipe with the same stages as those receipts, and no lab paths:
  1. fetch and hash-check;
  2. sources, via `prepare-gcc14-spe-candidate.py` and the glibc series;
  3. Linux UAPI headers from the locked Debian `linux` source;
  4. the C-only stage 1 compiler and libgcc;
  5. glibc 2.41;
  6. the final C/C++ compiler with shared libgcc, libstdc++ and libatomic.

  Pins and hashes come from `manifest.json`, `profiles/toolchain-bootstrap.json` and `profiles/debian-trixie.lock.json`. Every make step, install included, gets the `*_FOR_TARGET` tools. The SDK gains `PREFIX/powerpc-linux-gnuspe/bin/{ar,as,ld,nm,ranlib,readelf,objcopy,objdump,strip}`, the layout GCC's `-print-prog-name` searches and the same as `scripts/package-spe-host-toolchain.py`. It also gains `PREFIX/bin/powerpc-linux-gnuspe-<tool>` for autotools/meson `$host-tool` lookups. All of these link to Debian's `powerpc-linux-gnu-*` binutils 2.44.
- `docker/Dockerfile.gcc14-spe-sdk` is the build environment, on the same reviewed trixie digest as `Dockerfile.kernel`. It runs the recipe from the repository mounted at `/recipe`.

## Validation

The recipe was run end to end in a fresh volume, with only the download cache pre-seeded, from `development` 718abad (candidate 0001-0022): `WORK=/work/sdk CACHE=/work/cache`. It exited 0. A first run stopped at `headers_install` because `rsync` was missing; the Dockerfile now installs it, and the rerun resumed after the finished stages.

- `powerpc-linux-gnuspe-{ar,as,ld,nm,objcopy,objdump,ranlib,readelf,strip}` are on PATH from the SDK. `powerpc-linux-gnuspe-gcc -print-prog-name=ar|ranlib|nm|objdump|strip` resolves to `PREFIX/powerpc-linux-gnuspe/bin`. A compile, `ar`, `ranlib` and `nm` round trip works.
- Against the recipe-built SDK:
  - `check-gcc14-spe-candidate.py --qemu`: 22/22;
  - `check-spe-vec-perm-reduction`, `check-spe-tf-pack-overlap`, `check-spe-tf-fix-rounding` and `check-spe-tf-split-misaligned`: all pass;
  - `bench/spe-abi-smoke.c` and `spe-cxx-smoke.cpp`, static, on the A1222: `failures=0` both.

Limits:
- Debian SDK/runtime packaging stays with `scripts/package-spe-host-toolchain.py`.
- The recipe produces an install tree, not packages.
