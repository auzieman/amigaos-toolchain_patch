# First GCC14 sbuild consumer: zlib (#27) — 2026-11-16

With the GCC14 SDK qualified (`profiles/compiler-policy.json`, 8a18e48), the standard path (`run-sbuild-package.py`: mmdebstrap root, sbuild unshare, apt resolver) now builds powerpcspe packages from the GCC14 foundation only. Nothing from GCC8 was among the inputs.

Host: the Debian 13 WSL2 replica of the build host, laid out as on the R730 (`owner` account with subuid 165536+65536; base `/srv/data1/tabor-build/linux-live-001`; `tabor-{apt-cache,sbuild-repositories,sbuild-tmp}` beside it). `run-sbuild-package.py` and `build-frozen-buildd-root.py` ran unmodified.

## Chain

| step | how | result |
|---|---|---|
| buildd root | `build-frozen-buildd-root.py --lock profiles/trixie-spe-base.lock.json` (snapshot 20261102T220000Z) | `trixie-amd64.tar` sha256 `af29a74a910dae6e...`, native foundation versions as locked |
| UAPI | `run-sbuild-package.py`, spec = `profiles/sbuild/linux-uapi.json` with the local root | `linux-libc-dev_6.12.115-2+spe1_all.deb` |
| cross core | `build-cross-core-metapackage.py` with `packaging/tabor-spe-cross-build-essential` 1.0+spe8 (this commit) | `crossbuild-essential-powerpcspe_1.0+spe8_all.deb` |
| host helper | spec = `profiles/sbuild/dh-golang-host.json` with the local root | `dh-golang_1.63+spe1_all.deb` |
| zlib | spec = `profiles/sbuild/zlib.json`, extra inputs replaced by the GCC14 set below | zlib1g, zlib1g-dev, libminizip1t64, libminizip-dev, minizip `1:1.3.dfsg+really1.3.1-1` powerpcspe |

zlib's inputs were:
- `tabor-spe-toolchain 14.2.0+tabor1`, through `native_toolchain_inputs`. Its receipt sha256 `c6539872...` equals the policy's `qualified_sdk_receipt_sha256`, so the runner recorded `compiler: {gcc_major: 14, sdk_receipt_sha256: c6539872...}`.
- `libc6` and `libc6-dev` 2.41-12+deb13u4.
- The `tabor-spe-libgcc-s1`, `-libstdc++6` and `-libatomic1` runtimes, 14.2.0+tabor1.
- `linux-libc-dev 6.12.115-2+spe1`, the cross core and dh-golang above.

The specs and receipts actually used are in `specs/` and `*.receipt.json`. Their `work/...` receipt paths and hashes refer to this replica, so they are evidence, not R730 profiles.

## Checks

- sbuild installed `tabor-spe-toolchain (14.2.0+tabor1)` and `crossbuild-essential-powerpcspe (1.0+spe8)`; configure ran `--host=powerpc-linux-gnuspe` with `CC=powerpc-linux-gnuspe-gcc`.
- `libz.so.1`: ELF32 big-endian PowerPC, `Tag_GNU_Power_ABI_FP: hard float`; `zlib1g` `Depends: libc6 (>= 2.41)`.
- Under `qemu-ppc -cpu e500v2` with only the packaged libc6 and zlib, `minizip -9` compressed 3.5 MB of random data plus text, and `miniunzip` restored it byte for byte. The host's Python `zipfile` also reads and verifies an archive written by the SPE minizip.

## Changes in this commit

- `packaging/tabor-spe-cross-build-essential`, 1.0+spe8: depends on the GCC14 toolchain and runtimes (14.2.0+tabor1). `tabor-spe-libatomic-dev` is gone because the GCC14 toolchain ships `libatomic.so`/`.a` itself.
- `scripts/package-gcc14-spe-target-runtime.py`: the receipt uses the standard `debian-packages-built-not-target-installed` status, which the sbuild runner requires for extra inputs. The rebuilt runtime-002 has the same libraries (sha256) and payload listing as runtime-001.
- `scripts/fetch-locked-component.py` (new): fills an sbuild `source_cache` with one component from a lock, checked against size and sha256.

## Build-host notes

- `prepare-debian-build-host.sh` installed no sbuild tooling. It now also installs `mmdebstrap sbuild uidmap debhelper quilt` and, for Debian kernel control generation (UAPI), `kernel-wedge python3-dacite python3-jinja2 python3-debian`.
- sbuild runs as `owner`, so the runner must be started from a directory `owner` can enter. Starting it inside a private checkout fails with `BUILD_DIR directory ... does not exist`.
- `owner` must be able to write the cross-core output directory, since `dpkg-source` runs as `owner`.

## pkgconf and fuse3

Meson consumers need `pkgconf:powerpcspe`, which is Multi-Arch `same` and provides the triplet `pkg-config`. So `pkgconf 1.8.1-4` was built first, through the same path and the same inputs (`sbuild-pkgconf-gcc14-001`). It then joined fuse3's extra inputs.

`fuse3 3.17.2-3` was built twice with GCC14:

- **With the pinned #23 series** (`patches/fuse3/series.json`), as `sbuild-fuse3-gcc14-002`: it built fuse3, libfuse3-4, libfuse3-dev and fuse3-dbgsym, and the runner's payload inspection ran. The meson probe printed `Checking if "C++ 64-bit atomic operations" links: NO` and `Library atomic found: YES`, and memfs_ll linked with `-latomic` (`fuse3-atomic-probe.txt`). `libfuse3.so.3.17.2` is ELF32 PowerPC, NEEDED libc.so.6 only. Under qemu e500v2, `fusermount3 -V` prints `3.17.2` and `mount.fuse3` prints its usage.
- **Without the patch** (control), as `sbuild-fuse3-gcc14-unpatched-001`: memfs_ll fails to link with an undefined `std::__atomic_base<unsigned long long>::fetch_add` (`fuse3-unpatched-failure.txt`). That is the same failure #23 recorded under GCC8, so the patch is still needed with GCC14. A 64-bit atomic on 32-bit PowerPC is a libatomic call with either compiler.

## Remaining (#27)

- Larger consumers through this path (the libx11 and xcb sequence).
- A full (non-stage2) glibc.
- Physical A1222 runs of the dynamically linked packages.
