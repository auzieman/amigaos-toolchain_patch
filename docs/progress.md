# Engineering progress

This log records evidence rather than treating a successful source import as a
working toolchain. Raw generated source/build trees remain outside Git; patch
origins, source pins, run IDs and artifact hashes provide the replay path.

## 2026-10-30 — first Debian iterations

Target sources: Debian linux 6.12.113-1 and glibc 2.41-12+deb13u4.
Host/build environment: Debian trixie container on BKC lab-edge; PowerPC cross
compiler, 2 CPU / 4 GiB runtime. AmigaOS SDK integration remains a separate
contract; the current results concern Linux/SPE on A1222.

| Revision / run | Change and reason | Verified result / remaining work |
| --- | --- | --- |
| `5314411` | Pin Debian sources, add fresh extraction/re-patching runner and first component patches | Tabor machine/DTS patch plus preparatory 36-file glibc import. Neither patch initially proved a complete build. |
| `0fce93d7-aeb9-4fdf-9165-5a7b6834c10c` | First BKC attempt, unpacking on shared NFS | Tools image built. Unpack was I/O-bound and intentionally stopped; no compiler failure inferred. |
| `12c10c7` | Move active work to local disk with free-space guards | Preserve diagnostics and use fresh work for retries. |
| `23fa71a4-4dbb-49a3-9249-8333c3312e4b` | Apply patches to real Debian sources and cross-compile board targets | Tabor object and DTB passed; object is 32-bit big-endian PowerPC ELF. Full kernel interrupted because olddefconfig re-enabled DWARF. glibc patch applied but compiler rejected SPE flags. |
| `02cf5eb` | Select DEBUG_INFO_NONE explicitly and retain evidence before deleting disposable trees | Seven tests passed. Exact scoped artifact hashes: [first iteration receipt](builds/20261030-first-debian-iteration.json). |
| `4c8d17fa-5380-402a-ab11-42e9a528e19f` | Fresh retry with corrected config | Initial 4 GiB free-space guard stopped kernel extraction because duplicate staged archives consumed space. This is infrastructure, not a patch failure. |
| `b57b3f7b-cc3c-43b4-95a7-31b11186478b` | Replay from the canonical verified archive cache using a 150 KB project bundle | Fresh Debian extraction, local patches, DEBUG_INFO_NONE assertion and scoped board/DTB checks passed. Full vmlinux/modules/dtbs compile passed; collected artifact hashes verified. glibc compiler preflight remains failed. No board boot/ABI acceptance. |

The archive cache is now deduplicated independently of small project/patch
bundles. Cached archives remain hash-checked and read-only in containers;
every source/object workspace is newly created and re-patched. Completed-run
duplicate cache copies were compared before removal; the canonical cache and
local downloaded originals remain. An attempted bulk archival copy to NFS timed
out; no partially copied file is used as a verified cache entry.

## What reviewers can assess now

- Actual Tabor platform/DTS source changes and retained upstream notices.
- The recovered e500-only glibc files and their exact removal-history origin.
- Fresh-run logic, source/patch checksums and explicit failure handling.
- The compiler prerequisite: current Debian GCC rejects `-mabi=spe`, `-mspe`
  and `-mfloat-gprs=double`; modern SPE userspace is not working yet.

Full compile evidence: [Debian kernel receipt](builds/20261030-full-debian-kernel.json).

Next: QEMU e500v2 boot smoke test, then GCC SPE restoration
and the remaining glibc shared-state/configuration work. Kernel boot wrapping,
real A1222 serial boot, audio/power controls and runtime ABI tests remain pending.

## 2026-10-30 — QEMU boot accepted

Full Tabor kernel compilation passed independently. The initial minimal QEMU
profile required configuration dependency fixes; its first linked kernel was
silent because PHYS_64BIT/SERIAL_OF_PLATFORM were missing. Fresh attempt-005
with both enabled booted Linux 6.12.113 under QEMU 10.0.13/e500v2, brought up
two CPUs and reached freestanding PPC32 init. No panic during 60 seconds.
[Boot receipt](builds/20261030-qemu-boot.json) and
[serial proof](builds/20261030-qemu-serial.log) retain exact evidence. Artifact
manifest, kernel/config/init hashes verified; seven workflow tests pass.

Two desktop-4 capture windows show build/serial and an ANSI edge CPU/RAM
monitor. Guest metrics are explicitly pending. [E-Trixie follow-up](e-trixie-follow-up.md)
records the laptop-style live USB intent and direct SPE → SDL software →
SDL/GL → real A1222 AMD validation gates. No distribution image is built yet.

## 2026-10-30 — direct SPE arithmetic and graphics limits

The same booted QEMU kernel now runs a libc-free init executing known-result
single/double SPE additions and register load/store. Exact results passed;
serial/initramfs/source hashes verified and disassembly retained. See
[arithmetic receipt](builds/20261030-qemu-spe-arithmetic.json). Full ABI, glibc
and GL are still unvalidated. Desktop-4 monitor shows the narrower PASS.

[Minimal E/gears work](minimal-e-gears.md) records the unavailable edge GPU,
stock VirGL little-endian limitation, physical USB preference and a verified
staging bundle. No compatible rootfs/reference firmware packaging is currently
available, so no boot-ready USB or E/gears execution is claimed.
