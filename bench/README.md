# Freestanding fractal comparison

The Mandelbrot demo compares integer-only GNU soft-fp single-precision
operations with explicit SPE inline instructions, using the same bit-pattern
function interface, kernel, grid, escape algorithm, iteration cap and image
checksum. This is not a restored compiler SPE ABI/glibc benchmark.

Grid: 128x96, x starts at -2, y at -1.125, dx=dy=3/128, max iterations 96.
Each backend warms up once; three timed trials alternate backend order.
Guest CLOCK_MONOTONIC times rendering/checksum only, excluding serial image
transfer, boot and image presentation. Exact escape-count bytes must match.
QEMU TCG timings describe emulated execution, not physical A1222 performance.

Software helpers come from the already pinned NXP GCC 4.9.2 reference:
libgcc/soft-fp/{addsf3,subsf3,mulsf3}.c and headers,
libgcc/config/rs6000/sfp-machine.h, and include/longlong.h.
These retain LGPL-2.1-or-later notices with the stated additional linking
permission; inspect their original headers. Reference source is cached under
ignored sources/vendor/gcc-4.9.2, locked in profiles/vendor-sources.lock.json.
Record all used source hashes and exact compile command with each result.
No copied vendor runtime source is relabeled as original project code.

Build all C with -msoft-float and link without libc. Explicit efsadd, efssub
and efsmul are confined to the SPE backend functions; disassemble the executable
to check this and reject unexpected floating-point instructions elsewhere.
The existing GCC can assemble these instructions despite lacking an SPE C ABI
backend. This deliberately keeps the demonstration separate from that port.

The output contains per-trial guest microseconds/checksums and both raw image
buffers over serial. Host processing must verify all trials, image equality,
receipt/kernel hashes and intended instructions before producing a comparison
chart or speedup. Results are a demonstration, not GL acceleration evidence.

## Captured run — 2026-10-30

[ASCII timings](../docs/builds/fractal-20261030/results-ascii.txt),
[comparison graphic](../docs/builds/fractal-20261030/comparison.png),
[summary](../docs/builds/fractal-20261030/summary.json) and raw serial/disassembly
are retained together. Median guest render time: software 446.341 ms, SPE
173.063 ms, ratio 2.579... (displayed 2.58x). All 12,288 escape counts match;
all six timed render checksums are abd5de74. This is one emulated run, not a
physical performance claim or general estimate of SPE acceleration.

The initial run failed the clock probe using the legacy syscall and revealed
incomplete syscall clobbers. No result from that attempt is accepted. The
accepted run uses clock_gettime64 (403), a 64-bit timespec and an out-of-line
syscall wrapper with volatile GPR/CTR/CR0 clobbers. Time excludes boot, serial
transfer, palette generation and host-side PNG/SVG rendering. Both paths use
noinline arithmetic wrappers; the rendering algorithm is identical.

Replay inside the retained kernel/QEMU tools image, using fresh /out storage
and an unchanged pinned vendor reference mounted at /vendor:

```sh
mkdir /out/softfp
cp /vendor/libgcc/soft-fp/*.h /out/softfp/
cp /vendor/libgcc/soft-fp/addsf3.c /vendor/libgcc/soft-fp/subsf3.c /vendor/libgcc/soft-fp/mulsf3.c /out/softfp/
cp /vendor/libgcc/config/rs6000/sfp-machine.h /vendor/include/longlong.h /out/softfp/
cd /out
powerpc-linux-gnu-gcc -O2 -msoft-float -mcpu=8548 -ffreestanding -fno-stack-protector -I/out/softfp -c /out/softfp/addsf3.c /out/softfp/subsf3.c /out/softfp/mulsf3.c
powerpc-linux-gnu-gcc -O2 -msoft-float -mcpu=8548 -ffreestanding -fno-builtin -fno-stack-protector -fno-pie -msdata=none -nostdlib -static -no-pie -Wl,-e,_start -I/project/bench /project/bench/fractal.c /out/addsf3.o /out/subsf3.o /out/mulsf3.o -o /out/fractal-init
python3 /project/scripts/qemu-boot-smoke.py --kernel /kernel/vmlinux --init-binary /out/fractal-init --output /out/run-001 --timeout 90 --image-id sha256:RECORDED_IMAGE_ID
```

Mount project/vendor/kernel read-only, output writable; constrain Docker to two
CPUs, 2 GiB RAM and no network. Verify pinned vendor commit and used-file hashes
against docs/builds/20261030-fractal-inputs.json. The image used in the captured
run is recorded in its receipt, rather than inferred from a floating tag.
Disassemble with powerpc-linux-gnu-objdump -d -M e500. Only spe_add/spe_sub/spe_mul
may contain efs instructions; software helpers must contain no FP/SPE arithmetic.

scripts/fractal-report.py --run /absolute/collected/run --output /new/report
verifies the receipt/serial hash, completion marker, no failure marker, exact
trial coverage, image equality and FNV checksum before generating files.
Its host graphics use only Python's standard library. comparison.svg embeds
the original 128x96 PNG and scales it for presentation; it adds no computed
pixels or timing data. The PNG comparison was exported with host Inkscape.
