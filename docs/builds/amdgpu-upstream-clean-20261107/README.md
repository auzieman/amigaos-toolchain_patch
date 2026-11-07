# Fresh GitLab AMDGPU kernel control — 2026-11-07

User requested compilation of current upstream source to check whether earlier
experiments contaminated the driver. Pinned AMD development commit
5349075eac146ae0511d8929fc24451e4d9a4b7e (Linux7.3-rc6), previously verified
against the official drm/amdgpu/kernel drm-amdgpu-next ref.

Fresh detached full worktree and empty output directory on R730. No earlier
objects, experimental SMU/GFX/MQD patches or output tree reused. Shared Git
object cache avoids source redownloads. Only the two retained A1222 board
patches are applied. Their7.3 variant in patches/linux/upstream-7.3/ changes
only the Makefile context of the DTS registration to match its expanded file;
no hunk fuzz/dropping. Driver sources remain upstream.

Attempt001 stopped before compilation because the no-checkout worktree did
not materialize files. Attempt002 corrected checkout, then stopped on the
reviewed DTS Makefile context mismatch. Neither altered the reference tree.
Attempt003 applies the reviewed board patches and compiles in an isolated
4CPU/6GiB/network-none container using the existing pinned GCC14.2/binutils2.44
image. launch-on-r730.py retains the exact lab launch recipe; it refuses reused
work directories and is not an installer.

Input is the accepted6.12 modular configuration, migrated with olddefconfig.
LOCALVERSION changes to -tabor-upstream-001 to separate this kernel/module ABI.
This is a new-kernel experiment, not a refresh of the frozen Debian port base.
CONFIG_PPC32, SPE, SMP, HIGHMEM, PHYS_64BIT, TABOR, MODULES, VT, FB and
FRAMEBUFFER_CONSOLE remain enabled; DRM_AMDGPU is modular. Kernel builds are
freestanding and do not validate modern SPE glibc userspace.

Status: Kbuild completed exit0. vmlinux, modules and DTBs compiled; final
receipt records hashes and confirms drivers/gpu has no diff from upstream. This module cannot be inserted into the running6.12
kernel. Hardware/USB/U-Boot remain unchanged. Even if a later7.3 boot succeeds,
it will not alone prove which historical patch or kernel change caused the
6.12 failure; a matched-version clean control may still be needed.

User also authorizes libc/SDK updates if needed. Existing Trixie userspace target
is glibc2.41-12+deb13u4, with full runtime/package gates still open; GCC8.5/tabor6
remains the accepted SPE userspace compiler. The ordinary PowerPC GCC14 kernel
compiler does not restore a modern SPE userspace backend. A libc update is not
required for this freestanding kernel build. Audit/upgrade userspace separately
without changing this experiment's inputs midway.

## Verified completion

Kernel release7.3.0-rc6-tabor-upstream-001; all selected targets passed with
GCC14.2.0-19 and binutils2.44. Fresh output and no experimental GPU patches.
Receipt includes final configuration, vmlinux, Module.symvers, AMDGPU module
and Tabor DTB hashes. The full build log remains on R730 in the run directory.
The kernel is not installed or boot-tested. Pair this module with its own7.3
kernel/module tree; do not insert it into the running6.12 kernel.

Userspace follow-up is authorized but no libc version change was needed here.
The existing glibc2.41 SPE package/runtime acceptance and GCC14 SPE backend
restoration remain separate SDK work. No statement of their completion follows
from this freestanding kernel build.
