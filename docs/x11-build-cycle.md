# Active source-built X11 client cycle — 2026-10-31

R730 now runs a separate detached Docker job for the ordered X11 client chain,
using the tested software prerequisites as read-only inputs. The existing
interactive QEMU guest and desktop 4 noVNC stay running. This cycle builds
libraries and headers; it does not yet launch Xorg or E.

`profiles/x11-sources.lock.json` pins 22 Debian Trixie source packages in build
order: protocol/transport headers, pthread metadata, Xau/Xdmcp authentication,
XCB protocol generator and libraries, Xlib, extensions and selected XCB utils.
Only sources are fetched; all target ELF output is compiled with the isolated
GCC8.5 SPE reference tools and experimental restored glibc sysroot. Native
Python runs the architecture-independent XCB generator, distinct from PPC
runtime libraries. Archives and DSCs are hash checked; independent OpenPGP
signature verification is not claimed. Source license notices are preserved.

`build-x11-clients.py` refuses a reused work directory, extracts Debian source
and applies its package changes freshly. Target pkg-config searches only the
new stage. Explicit e500v2/SPE/long-double flags, compiler/recipe hashes,
per-component state, command logs and final PPC32 big-endian ELF hashes are
recorded. The tested base stage, tools and sysroot are read-only; only the new
work stage is writable. The container runs offline, four CPUs / four make jobs,
6GiB memory; native tooling image is pinned to
`sha256:eb877fcd41042f17c0a1f67aa6e679c8dc81c10a72bf3ad12287d864e5eacdf0`.

Iteration001 built xorgproto and xtrans but stopped on a packaging assumption:
libpthread-stubs ships `debian/copyright.debian`, not `debian/copyright`.
Iteration002 collects those notices plus upstream COPYING/COPYRIGHT and starts
from fresh source. The failed receipt is retained. Launch snapshots are
historical; inspect current receipt/container state for completion.

R730 paths: `/srv/data1/tabor-build/linux-live-001/work/x11-clients-002`,
container `tabor-x11-002`. `receipt.json` is atomically updated with active
component/status. Docker logs have BUILD_START/BUILD_PASS checkpoints; build.log
has actual configure/compiler output. The desktop 4 log viewer follows only
the newest iteration and displays its receipt status, rather than showing old
fatal errors without their iteration context. It continues watching after a
build ends; that alone does not mean compilation is active.

Still required: X11 runtime/link checks, font dependencies, native EFL generators,
EFL/E/Terminology and Xorg server plus display/input drivers. Keep the floating
rounding failure, full ABI gate and physical U-Boot/HDMI validation explicit.

## Follow-up: complete client chain and protocol proof

Fresh iteration002 failed at Xlib linking: installed libxcb libtool metadata
contained an absolute `/usr/lib/libXau.la` dependency that bypassed the target
stage. Iteration003 removes installed public-library `.la` files from the new
stage (including inherited libpng metadata), retaining their path/hash in the
receipt. This follows [Debian shared-library policy](https://www.debian.org/doc/debian-policy/ch-files.html).
These public libraries are not libltdl plugins; this is not a blanket rule for
all future plugin metadata. Accepted input stages remain unchanged.

Xlib then built. Iteration003 next stopped at libXext's configure run-test for
zero-size allocation while cross compiling. `bench/x11-alloc-check.c` reproduces
the exact configure predicate: **any** of malloc(0), realloc(malloc(10),0), or
calloc(0,10) returning NULL. SPE guest measurements were 0/1/0 respectively,
so the measured answer is yes. This is scoped in
`profiles/x11-configure-cache.json`, hash-pinned by the runner; it is not guessed
from host libc or generalized to another target sysroot.

Fresh iteration004 finishes all 22 components and verifies 48 staged ELF files
as PPC32 big-endian. Receipts, failed log excerpts, allocation proof and build
checkpoints are under [retained evidence](builds/r730-x11-20261031/completed-004.json).
No upstream source, compiler/backend or libc patch was necessary for these
build-system failures. Nonfatal compiler/documentation warnings are retained.

`build-x11-client-probe.py` links the client test with the resulting target
libraries and checks every recursively needed shared object before staging a
stripped runtime closure. `probe-x11-client.py` uploads those files to a unique
ordinary-user guest directory; LD_LIBRARY_PATH affects only this invocation.
The existing guest rootfs/system libraries and physical USB remain unchanged.

Actual SPE QEMU execution passes:

- Xlib creates/fills a pixmap and reads back every pixel accurately.
- Render/RandR/XFixes version query/replies succeed.
- A separate XCB connection completes its request/reply.

[Raw protocol output](builds/r730-x11-20261031/protocol-guest.log) and
[runtime receipt](builds/r730-x11-20261031/protocol-receipt.json) distinguish this
from target Xorg acceptance. The server was native amd64 Xvfb in a separate
container, image
`sha256:7173c89674284fe014d0ffafb6d603f2e5d698577fe89882ce20a84c2e1a31fb`;
its package versions are retained. It ran as display117, 640x480x24, TCP6117,
published only on R730 loopback127.0.0.1 with access control disabled for this
isolated lab probe. QEMU user networking reaches that endpoint at10.0.2.2:117.
The server container is stopped after the probe. Native server Mesa dependencies
are test tooling only; none enter the SPE runtime payload or qualify target GPU.

GitHub issues: [libtool path](https://github.com/auzieman/amigaos-toolchain_patch/issues/1),
[allocation configure check](https://github.com/auzieman/amigaos-toolchain_patch/issues/2),
[unresolved fenv arithmetic](https://github.com/auzieman/amigaos-toolchain_patch/issues/3).
The first two have passed their selected build/protocol validation. The third
remains open. Xorg server/drivers, native EFL generators, fonts and E desktop
still need their build/runtime stages; no physical display or full ABI claim.
