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

Next: full kernel compile with no debug information, then GCC SPE restoration
and the remaining glibc shared-state/configuration work. Kernel boot wrapping,
real A1222 serial boot, audio/power controls and runtime ABI tests remain pending.
