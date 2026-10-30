# Minimal A1222 E/Trixie package plan

Canonical candidate seed: [profiles/images/a1222-minimal.json](../profiles/images/a1222-minimal.json).
This is a **fresh-build plan**, using our eventual restored SPE compiler/glibc
sysroot and selected trixie sources. It is not a copy of old Tabor Linux, an
amd64 installation recipe, a resolved package lock or a completed image.
A minbase-equivalent rootfs and all transitive dependencies must be rebuilt for
one consistent ABI. Standard trixie package names do not imply official
powerpcspe binaries exist. libc/libgcc/libstdc++ must come from our toolchain.

| Increment | Explicit additions beyond preceding stage | Pass condition |
| --- | --- | --- |
| Serial rescue | minbase-equivalent, systemd-sysv, udev, initramfs-tools, kmod, iproute2, ifupdown, dhcpcd-base, procps, pciutils, usbutils, less, nano, sudo; project SPE/fractal/ASCII tests | Real serial login; detect RAM, devices and network; direct SPE checks pass |
| E desktop | xserver-xorg-core, xserver-xorg-input-libinput, xinit, xauth, dbus-user-session, libpam-systemd, enlightenment/data, terminology, fonts-dejavu-core | Console login then startx brings up E, terminal, keyboard and mouse |
| GL test image **(first desktop target)** | libgl1, libglx-mesa0, libgl1-mesa-dri, libegl1, libegl-mesa0, mesa-utils, libdrm-tests, htop; exact Radeon driver/firmware overlay | Capture GL identity, DRM logs, glxgears output and CPU/SPE results |
| Browser **(optional later)** | firefox-esr, ca-certificates, fonts-liberation and mandatory dependency closure | Browser toolchain/architecture feasibility, local page, then TLS page |

These are explicit seeds, not the complete rootfs contents. Required EFL,
Mesa/Gallium, X11, D-Bus/PAM, input, font/codec and C/C++ runtime dependencies
remain. Do not promise an image size or idle-RAM figure before resolving and
measuring a target build. No compiler/build farm belongs in the live runtime.

## One normal login

One human account, `tabor`, with a provisioning-time password; normal service
accounts remain. Login on tty1, run `startx`, and start `enlightenment_start`
through the user session. Use logind/PAM and the user D-Bus session for access
to the seat. Keep serial rescue access. No display manager or automatic login
is needed for the first image; no password is stored in the repository.
This is a normal desktop session, not systemd rescue/single-user mode.
Use one init/udev/logind stack rather than developing custom session plumbing.

## 8 GiB and the Radeon card

Treat 8 GiB as the requested hardware target, not a measured property of our
board. Confirm original A1222 versus A1222+ revision, DIMM/firmware detection
and the device-tree memory map. Validate CONFIG_PHYS_64BIT and the applicable
PPC32 HIGHMEM/memory configuration before claiming use of RAM above 4 GiB;
review any inherited mem=3500M cap. Physical addressing and user virtual
addressing are different: 8 GiB system RAM does not give a single PPC32 process
an 8 GiB address space. Do not change firmware memory defaults without evidence.

Identify the exact Radeon PCI ID before choosing kernel `radeon`/`amdgpu`,
Mesa `r600`/`radeonsi`, firmware subset and any LLVM requirement. The generic
Xorg modesetting driver is the first candidate; a separate vendor DDX package
is conditional. Do not include every Radeon generation by default or assume
all Radeon models work with PPC32/SPE. Kernel DMA/IOMMU/SWIOTLB, PCI resource
windows and firmware loads must be tested on the board.

QEMU retains a separate virtio-2D/software-Mesa configuration. The known
big-endian VirGL limitation and lack of GPU assignment to edge remain recorded
in [minimal E/gears status](minimal-e-gears.md). Physical GL acceptance must
show the real Radeon renderer, not an unreported software fallback.

## Keep the first image small

Use no recommends/suggests after explicitly identifying needed runtime pieces.
Start with one locale and font family, bounded volatile logs, wired DHCP and
manual desktop startup. Omit desktop task packages, a greeter, printing,
Bluetooth daemons, discovery services, Flatpak/Snap, multimedia suites and a
browser from the first GL-test image. A mandatory library dependency may still
remain even when its associated daemon is absent.

Drop package archives, build headers/tools and bulk documentation from the
runtime, retaining licenses, required runtime assets and diagnostics. Do not
trim firmware or modules by filename guesswork. No default persistent overlay,
swap or internal-disk installation is planned. Resolve sizes/dependencies and
record a full package/file/hash manifest before choosing the USB layout.

LAN SSH and x11vnc are optional debug overlays, not default listeners. Bind a
future VNC service to loopback and use the existing LAN SSH tunnel approach;
reuse the same active E session for physical capture. SDL is a later optional
smoke test. The existing fractal init needs a normal CLI entry/exit wrapper
before it can be shipped as an ordinary test application in this rootfs.

Firefox is deliberately a final increment: the selected release's supported
architectures, Rust/LLVM target, SpiderMonkey/JIT/interpreter, C++ runtime and
sandbox requirements must all be qualified. Its upstream binary is not an SPE
binary. Do not disable sandboxing or ship an obsolete browser simply to claim
it launches. It must not delay the serial/E/gears milestones.

## Intake and versioning

Checked trixie package identities against official package pages and cached
amd64 apt metadata in the lab tools container. That check establishes naming,
not target availability or a target dependency solution. `mesa-utils-extra`
has no candidate in that metadata and is not used. `firmware-amd-graphics` is
in non-free-firmware and was verified through its official package page; its
absence from the main-only lab cache is not absence from Debian.
Before building: choose exact source revisions, pin hashes/licenses, resolve
our target dependency graph and verify libc/compiler prerequisites. systemd
also requires a suitably configured kernel; the tiny QEMU smoke config is not
assumed sufficient for this desktop stack. No source/runtime build or USB write
was started by this package-list change.

Sources checked 2026-10-30:

- [Enlightenment](https://packages.debian.org/trixie/enlightenment), including its mandatory runtime dependencies.
- [Mesa utilities](https://packages.debian.org/trixie/mesa-utils): glxinfo and glxgears.
- [DRM tests](https://packages.debian.org/trixie/libdrm-tests).
- [AMD firmware](https://packages.debian.org/trixie/firmware-amd-graphics).
- [systemd-sysv](https://packages.debian.org/trixie/systemd-sysv).
- [Firefox ESR](https://packages.debian.org/trixie/firefox-esr); listed package architectures do not establish SPE support.
