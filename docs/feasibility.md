# Source-backed feasibility — 2026-10-30

| Component | Evidence | Consequence |
| --- | --- | --- |
| GCC SPE | https://gcc.gnu.org/legacy-ml/gcc-patches/2018-04/msg00810.html and https://doc.rust-lang.org/rustc/platform-support/powerpc-unknown-linux-gnuspe.html | GCC 8 obsoletion / GCC 9 removal; modern GCC restoration is its own backend maintenance task. |
| glibc SPE | https://ecos.sourceware.org/ml/glibc-cvs/2019-q2/msg00204.html | Removal commit a053e878494080f7070cf92890e546057236c9c9 deletes e500 sysdeps and state preservation, not merely a configure check. |
| glibc release boundary | https://sourceware.org/legacy-ml/libc-alpha/2019-05/msg00364.html | SPE removal boundary is 2.30. Historical 2.29-family source is a reference, not a recommended production runtime. |
| ABI specification | https://www.nxp.com/docs/en/reference-manual/E500ABIUG.pdf | Primary reference for calling conventions, register use, varargs and data layout; verify applicable e500 revision details. |
| Kernel compilation | https://docs.kernel.org/kbuild/llvm.html | Kernel toolchain path can be established separately; general powerpc support does not prove A1222 configuration support. |
| Local vendor board input | ../tabor-linux-forge, inventory in intake.json | Existing board/audio/DTS patch for v5.4-rc3; not a glibc or GCC SPE restoration patch. |

Inspected local vendor/patch directories and SDK filenames for SPE, glibc,
e500 and compiler patches. No matching Freescale/NXP SPE restoration sample
package was established in that bounded search. This is not an exhaustive
search of all connected repositories or archives. The exact vendor package,
license and Hyperion patch information still need locating. Do not infer a
license from a vendor download or mix unrelated Arm SPE or e500mc material.

Existing 6.6 profile tracks a moving branch; it is not an immutable build lock.
The next build must pin its actual kernel commit and compiler/container digest.
Existing fetch helper resets/cleans its build tree, so do not run it against
valuable source work. Use a fresh isolated source workspace instead.

The SDK currently present includes newlib/clib4 paths; these names alone do
not establish the requested future SDK's runtime or ABI. Confirm with Hyperion's
actual build contract before claiming glibc integration.
