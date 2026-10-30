# Freescale / NXP source intake — 2026-10-30

The A1222 target is Freescale QorIQ P1022 / e500v2. NXP is the current vendor.
This is not an Arm Layerscape platform; similarly named SDKs are not equivalent.
Primary vendor references:
- https://www.nxp.com/products/P1022
- https://www.nxp.com/products/processors-and-microcontrollers/arm-processors/layerscape-processors/linux-sdk-for-qoriq-processors:SDKLINUX
- https://github.com/nxp-qoriq-yocto-sdk (NXP-domain-verified organization)

## What we had

Existing tabor-linux-forge has the upstream 5.4-rc3 source, A-EON board/audio
patch, Tabor DTS/config and an adapted worktree. These are preserved unchanged.
A bounded filename inventory of Projects/Downloads (five levels, excluding
large recovery/cache directories) did not establish an existing vendor SDK
archive. Seagate/unmounted media and all repository histories were not searched.

## Now downloaded

Ignored sources/vendor/ contains these clean, shallow Git checkouts. Exact
commits, tree IDs and inspected-file hashes are in
../profiles/vendor-sources.lock.json. Each repository passed connectivity fsck.

| Checkout | Use and qualification |
| --- | --- |
| gcc-4.9.2 | NXP historical GCC; rs6000/spe.md, linuxspe.h and related SPE code present. GPLv3 plus runtime exception/material-specific notices; preserve per-file terms. |
| eglibc-2.19 | NXP historical runtime; e500 fenv implementations and context-e500.h present under libc/sysdeps. libc/COPYING.LIB is LGPLv2.1; other code/tools have their own notices. |
| linux-sdk1.7 | Historical NXP SDK kernel; exact SRCREV matches the retrieved SDK1.7 Linux recipe. GPLv2 kernel and file-specific notices. |
| u-boot-sdk1.7 | Historical matching-named SDK branch with P1022DS configuration. Licenses/README and file-level notices apply; not an A1222 bootloader replacement. |
| meta-fsl-ppc-sdk1.7 | P1022DS config requires e500v2.inc; board/kernel recipes retained. Layer/recipe/source licenses must be distinguished. |
| meta-fsl-ppc-toolchain | Historical external gnuspe compiler integration recipes, from a different-era branch. Not proof of a coherent SDK1.7 build. |
| fsl-yocto-repo | Vendor manifest history reference. Retrieved default manifest is a later revision, not asserted to match these historical trees. |
| boot-format | Vendor SD/SPI image tool and P1022DS reference configs, GPLv2. Reference only: no media-writing execution performed. |
| flib | Freescale SEC/crypto library, BSD-3-Clause or GPL-2.0+ notice. Not an SPE floating-point runtime; fetched for classification, not selected for integration. |

These are reference sources, not a complete SDK download or tested compiler/
libc/kernel combination. Remaining SDK dependencies include exact binutils,
Poky/BitBake layers, other recipe sources and host build dependencies. Select
one historical build manifest and close its dependency set when reproducing
that SDK. The first modern kernel build can instead use the separate pinned
kernel-tooling lane. No proprietary CodeWarrior or Hyperion source acquired.

## Repeatable check / fetch

From this project, run `python3 scripts/fetch-vendor-sources.py --check-only`.
Omit --check-only to download missing trees at their recorded immutable commits.
Existing changed trees are preserved and rejected, never reset or cleaned.
Complete upstream license files remain in the ignored checkouts; the enclosing
project does not relicense these repositories.

NXP's SDK page recommends community kernel/U-Boot sources for ongoing P-series
work. Vendor trees remain valuable historical comparisons, not current security
baselines. Compare specific SPE/board changes before forward-porting; do not
blindly overlay the vendor SDK on modern sources.

Documentation note: direct downloads of the NXP e500 ABI and SDK1.4 integration
PDF URLs returned HTTP 404 in this session despite indexed content. No local PDF
copy is claimed. The vendor code clones themselves completed successfully.
