# AmigaOS Docker/SPE fractal experiment

Branch: `amigaos/docker-spe-fractal`. Linux glibc and board patches remain
separate. This slice fixes a GCC6 image's assembler selection and supplies an
AmigaOS executable; it does not restore SPE to modern GCC.

## Verified configuration fixes

The inspected GCC6 driver `asm_cpu` specs map `8540` to `-me500` but omit `8548`.
With `-mcpu=8548`, the compiler emits `isel` and its assembler rejects it.
`docker/amigaos/e500v2.specs` preserves the complete existing spec and adds only
`8548` → `-me500x2`. The derived image's gcc/g++ wrappers supply this overlay;
PATH and CC/CXX point to them. Absolute calls to the original compiler bypass
the overlay. The installed compiler files and other CPU mappings are untouched.

The SDK has no newlib `lib/soft-float` directory. Passing `-msoft-float` at final
link incorrectly selects that absent library directory for this workload.
The CLI is therefore compiled/linked on normal newlib ABI with integer/pointer
interfaces to the arithmetic modules. Only the original GNU soft-fp helpers and
their wrappers use soft-float C internally. Their symbols are privately renamed.
No float or double crosses the runtime/module boundary. This is not a repair of
general SPE C ABI interoperation with arbitrary runtime libraries.

## Replay

The profile pins both the GCC6 reference and a GCC13 comparison image by amd64
manifest digest. Pulling images is a separate intake operation. The source
helpers are the exact files/hashes in `profiles/amigaos-docker-spe.json`, retained
from the existing pinned NXP GCC reference. Preserve their original license
notices; the original source has LGPL-2.1-or-later plus its linking permission.
No SDK or vendor runtime sources are copied into this repository.

On an authorized Docker host, with images already pulled:

```sh
docker build --network=none --pull=false \
  --build-arg AMIGAOS_TOOLCHAIN_IMAGE=walkero/amigagccondocker@sha256:10fdc756661c7494946f91fdec252b91ac1d99dd3f26629ba848a753221dde7f \
  --iidfile /tmp/tabor-os4-fixed-image.id docker/amigaos
sudo python3 scripts/run-amigaos-docker-test.py \
  --project "$PWD" --softfp /path/to/verified/softfp \
  --image "$(cat /tmp/tabor-os4-fixed-image.id)" \
  --output /path/to/fresh/run-001 --uid 1000 --gid 1000
```

The runner refuses an existing output directory and requires an image digest or
local image SHA256 ID. It uses two CPUs, 4GiB, no network, an unprivileged user,
a read-only root filesystem/inputs and writable output/tmp. Compiler version,
target, commands, source hashes, object disassembly, binary hash and failure or
success receipt are retained. No AmigaOS executable is run inside Linux.

Tests cover float/double SPE code generation and object assembly, C++ SPE object
assembly and preserved generic750 assembler mapping. These are compiler checks,
not C++ runtime/unwinding or full ABI acceptance. The own-object audit rejects
SPE and conventional FPU instructions outside the explicit SPE module; prebuilt
newlib/startup code is outside that audit.

## Board test and current limits

Copy `fractal-os4` into a writable test directory. Default execution is software
only and writes `fractal-soft.pgm`. The optional `--spe` switch compares software
and explicit native SPE and writes both PGM images. Use that switch only on an
appropriate SPE machine/OS; do not execute it in the Sam460 AmigaOS QEMU guest.

Each of three alternating trials renders the same 128x96 grid 16 times; one
untimed warmup per active path precedes timing. Each trial must checksum to
`abd5de74`; comparison mode additionally requires byte-identical count buffers.
Timing is C `clock()` CPU-time ticks per batch, not Linux wall-clock microseconds.
The run fails if the clock is unavailable, wrapped or too coarse. It excludes
printing and image writes. No AmigaOS timing or speedup is reported before an
actual captured board run. Runtime timing behavior must be confirmed on target.

This is single-threaded, so SMP/multicore support is unnecessary. Whether the
installed OS preserves SPE state across context switches, handles exceptions,
or supports a broader floating C ABI remains separate; this demo cannot certify
those properties. An updated OS is not assumed necessary or sufficient.

The host-only reference uses the host's native float instructions, explicitly
labels itself and refuses `--spe`. Its checksum/image test validates the shared
algorithm/output only. It is not the target soft-fp benchmark or an AmigaOS result.

Lab artifact: `ftp.lab.auzietek.com`,
`downloads/amigaos-fractal-20261031/` (lab/LAN only), with README and SHA256SUMS.
No executable is committed to Git. Test evidence lives in
`docs/builds/amigaos-docker-20261031/`.

## Captured compiler matrix — 2026-10-31

| Image / run | Observed result |
| --- | --- |
| Original GCC6 / gcc6-001 | Missing8548 assembler mapping rejects generated isel. |
| Manual e500 assembler flag / gcc6-002 | Arithmetic compiles; blanket soft-float final link cannot find newlib libc. |
| Derived GCC6 overlay / gcc6-006 | Float/double and C++ SPE objects assemble, generic750 mapping preserved, fractal links and own-object audit passes. |
| Original GCC13.5 / gcc13-001 | Rejects mabi=spe/mspe/mfloat-gprs, but explicit SPE integer-interface fractal compiles, links and passes own-object audit without the GCC6 overlay. |

The GCC13 result is useful even while native SPE C ABI support is absent. The
two native executables are staged on lab FTP: `fractal-os4` is GCC6 and
`fractal-os4-gcc13` is GCC13. Both remain unexecuted on AmigaOS. Keep separate
output directories when testing them. Neither build uses our Linux glibc patches.
