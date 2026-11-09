# Physical A1222 SPE fractal on the working framebuffer

On complete kernel `6.12.113-tabor-e2e-007`, the existing `/bin/fractal-test`
produced identical12,288 escape counts for integer GNU soft-fp and explicit
SPE single-precision operations. The same grid/iteration cap and arithmetic
interfaces are documented in `bench/README.md`. All six timed checksums are
`0xabd5de74` and the physical program reports PASS.

| Path | Three render times, microseconds | Median |
| --- | --- | --- |
| Software floating point | 125590,125574,125547 | 125574 |
| Explicit SPE | 23846,23853,23845 | 23846 |

The median ratio is5.266 for this small128x96/96-iteration workload. Timing
excludes transfer, palette and display. This is not a general compiler ABI,
glibc, whole-system or GPU acceleration benchmark. Raw output is retained in
`fractal-physical.txt`, numeric results in `summary.json`, and the verified
escape-count bytes in `escape-counts.bin`.

`bench/fb-fractal.c` is an integer-only freestanding PPC32 presenter. It queries
the existing fbdev geometry, accepts the tested32bpp truecolor layout, verifies
the count range and expected checksum, and scales the data8x using nearest
neighbour into a centered1024x768 rectangle. It backs up every affected console
pixel before drawing and verifies every written byte by framebuffer readback.
It uses ordinary `/dev/fb0` reads/writes; it does not bind the GPU, issue GPU
commands, change modes or call a3D API. The framebuffer helper owns propagation
to the display; readback alone does not establish visible scanout.

The exact executable first passed a QEMU e500v2 regular-file fixture on the
R730: the whole8MiB-sized mode buffer matches an independent native-BE pixel and
offset model, restore matches the original byte-for-byte, and invalid escape
counts are rejected before backup or drawing. Disassembly contains no FP/SPE
instructions in the presenter. Source/binary hashes are in `fixture-receipt.json`.
The actual computation uses SPE in the separate, existing benchmark.

The physical presenter reports the actual1920x1080/32bpp/stride7680 mode, native
channel offsets red16/green8/blue0, then `FB_FRACTAL_DRAWN ... readback=PASS`.
See `physical-info.txt` and `physical-draw.txt`. The user confirmed: **"Yes, fractal looks correct"**. Physical visual
presentation therefore passes separately from the already accepted readable console.

All new runtime files are in tmpfs `/run`; the USB root remains read-only.
The old console pixels are retained only on the machine, not uploaded or
published. Restore the rectangle when desired:

```sh
/run/fb-fractal --restore /run/fractal-console.backup
```

The graphical data is enlarged from the measured128x96 result; it is not a new
1024x768 Mandelbrot computation. GFX IB timeout-110 remains open in canonical
issue28 and forge issue1. This demo establishes CPU/SPE computation and fbdev
presentation, not accelerated GPU rendering.
