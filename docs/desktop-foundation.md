# R730 foundation for the VM132-style A1222 image

The user confirmed the larger Linux USB target should move toward VM132.
R730 `linux-live-001` now has a tested reference C++ runtime and pinned desktop
source seeds. This is a concrete build prerequisite checkpoint, not a completed
E desktop. The existing written SanDisk remains the prior rescue increment.

## What now works

The earlier reference compiler was C-only and configured without a Linux C++
runtime. `bootstrap-spe-compiler.py` now supports an explicit runtime sysroot,
C/C++ languages and bounded jobs while retaining its original C-only defaults.
It re-extracts pinned GCC 8.5, configures SPE hard float with 128-bit long double,
builds libgcc/libstdc++, checks the unchanged read-only input sysroot and hashes
the installed tool tree and selected binutils. This remains historical GCC8
reference tooling, not modern GCC SPE restoration.

`cxx-reference-001` built the frontends but failed because the target-named
archiver was missing. Fresh `cxx-reference-002` adds private target binutils
aliases and PATH, then compiles and installs both runtime libraries. Neither
iteration changes the accepted C-only tools or original sysroot.

The [static probe](builds/r730-desktop-prerequisites-20261031/cxx-abi-002/receipt.json)
passes long-double size, exception/RAII unwinding, thread-local state and
concurrent uint32 atomics. The first static probe passed unwinding, then panicked
because a weak pthread_join reference was not pulled from static libc; retained
disassembly shows a branch into the ELF header. The corrected static link
explicitly retains pthread entry points. The source checks remain unchanged;
this is not a compiler/backend source patch or evidence for all atomics.

A second probe uses the real shared loader, glibc, libm, libgcc_s and libstdc++.
`build-cxx-live-payload.py` verifies every file is big-endian PPC32, follows all
DT_NEEDED entries, rejects libraries outside the reviewed tools/sysroot, and
stages stripped runtime copies. The loader path is `/lib/ld.so.1`.
`extend-rescue-initramfs.py` can add this checked payload to an already-verified
rescue archive without replacing existing files. The resulting RAM filesystem
is 25,077,256 bytes; no compiler, headers or build tools enter that runtime.

[network-probe-004](builds/r730-desktop-prerequisites-20261031/network-probe-004/receipt.json)
boots this filesystem with the same live QEMU kernel. Native laptop SSH verifies
login/PTY and executes the shared C++ CLI: all four checks PASS. Existing
fractal equality and eight basic C checks still pass; fenv remains FAIL.
No full ABI, arithmetic trap coverage, uint64 atomics or physical-board claim.

## Desktop sources and the lean first configuration

The VM132 reference contains 2,337 installed package records, much more than
our intended minimal target. Selected source versions are retained in
[reference metadata](builds/r730-desktop-prerequisites-20261031/vm132-source-reference.json).
Only functional choices are taken from this amd64 VM; its binaries are not
used in the PPC/SPE rootfs.

The exact EFL 1.28.1-1, e17 0.27.1-1 and Terminology 1.14.0-1 Debian DSCs and
payloads are downloaded and hash-verified on R730. Canonical inputs are in
[desktop-seeds.lock.json](../profiles/desktop-seeds.lock.json). The intact cache
is approximately 555 MiB, mainly source/assets, not measured installed size.
Debian copyright metadata and control/build dependencies were inspected. The
sources contain mixed BSD, GPL/LGPL and other notices; preserve per-file
licensing and font notices. No blanket license is assigned. Independent archive
signature verification is not claimed.

[The EFL candidate](../profiles/images/efl-x11-candidate.json) uses real option
names from this exact source: software X11, OpenGL/Wayland/DRM off, no audio,
media backends, physics, bindings, tests/examples or docs. Native architecture
optimization is disabled for cross compilation. Unlisted defaults still need
review; this is not a successful Meson configuration or resolved dependency
closure. Keep normal target init/seat/session policy from the package plan.

The Debian cross metadata explicitly lists native eolian/eet/edje/elementary
generators. These must run on the x86 host independently of PPC libraries.
X11, font/image, crypto and session dependencies still need exact locks and
source builds. Do not infer that disabling optional features removes those
mandatory dependencies. Mesa's [upstream compiler guidance](https://docs.mesa3d.org/install.html)
also cautions that some components require versions beyond its general GCC8
minimum; the selected driver/LLVM stack remains to qualify.

## Repeat and continue

Use the reviewed container identity and mounts described in
[r730-live-image.md](r730-live-image.md). Typical compiler arguments inside the
container (fresh paths required):

```
python3 /project/scripts/bootstrap-spe-compiler.py \
  --project /project --cache /cache --work /work/cxx-reference-N \
  --prefix /tools/cxx-reference-N --runtime-sysroot /sysroot \
  --languages c,c++ --jobs 4 --image-id sha256:REVIEWED_IMAGE_ID
```

`spe-cxx-smoke.py` tests static runtime execution. For shared execution, build
with `build-cxx-live-payload.py`, extend the full rescue archive, run
`qemu-live-network-probe.py`, and invoke laptop `probe-live-ssh-client.py --cxx`
through a loopback SSH forward. Retain client proof, stdout and all receipts.
The server receives only the operator public key; private keys stay local.

The new `usb-cxx-image-001/a1222-hardware-rescue.img` on R730 packages the same
physical kernel with this shared-runtime initramfs. U-Boot CRC/decompression
and FAT boot-file readback pass. This candidate has not been written to the
SanDisk or booted on the A1222 and still has no E desktop. Its receipt is
[retained here](builds/r730-desktop-prerequisites-20261031/usb-cxx-image-001/receipt.json).

Next build slice: resolve the software-X11 EFL dependency closure and native
code generators, then build E/Terminology and Xorg. Keep the existing physical
boot/native ABI trial available in parallel. Mesa/GPU integration stays behind
the floating ABI gate in the SPE workflow; [rounding diagnostics](fenv-rounding.md)
remain explicitly failed under QEMU. Do not label this checkpoint a finished
VM132-equivalent image or silently substitute generic PowerPC binaries.
