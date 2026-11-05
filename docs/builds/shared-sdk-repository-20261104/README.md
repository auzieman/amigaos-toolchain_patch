# Shared compiler and apt archive transport

The selected workstation queue contains110 sources, with four dependency-ready
R730 jobs at most. Round020 continues with its immutable inputs. Waiting021
was cancelled before any workers and replaced by022 after020, preserving all
source fixes and the full scope.022 selects the qualified shared-SDK root and
standard sbuild --extra-repository transport. Full sbuild integration results
remain pending; namespace/apt/compiler checks below have passed.

The real tabor6 compiler package was installed once with normal apt/dpkg in a
frozen native buildd root, using cached archives and disabled networking.
The new root archive retains installed package metadata, wrapper symlinks,
native runtime dependencies and ordinary Debian state. Its compiler payload
is excluded because an identical, hash-verified filesystem is mounted at
/usr/lib/tabor-spe-toolchain. This is a separately mounted package filesystem,
not a fabricated installed record or a replacement compiler wrapper.

Actual sbuild UID mappings, pivotroot and bind backend verified:
- dpkg-query reports installed8.5.0+tabor6; dpkg -V reports no SDK mismatch.
- A write fails specifically with Read-only file system.
- The compiler emits efsadd through that mount; no target program was run.
The mount guard can restore and verify the read-only mount after reboot.
The normal installed-package build roots and source/output trees remain
separate and writable where Debian requires them.

The target dependency archive remains complete: no trimming to one dose
installation set. dpkg-scanpackages --multiversion generates an immutable flat
apt repository from already verified inputs; sbuild's documented extra
repository and bind-mount options expose it. Apt chooses and installs actual
Build-Depends. The local trusted repository relies on our pinned input hashes;
it does not disable signature checking for the frozen Debian repositories.
730-artifact qualification passed with networking disabled: apt indexed the
bound archive, downloaded the requested SPE package, and its bytes match the
manifest. Mapped namespace root cannot write the archive. Two focused tests
verify repository reuse and rejection of payload corruption. Full package
integration acceptance remains pending in022.

Retained setup corrections: root001 could not traverse the private project
parent under mapped UID; subsequent roots use an external namespace-accessible
staging path and stream the tar.002/003 lacked usable native package indexes
(the limited local apt update cleaned other lists);004 preserves qualified
frozen indexes with standard apt list-cleanup configuration. Apt then installed
the actual SDK and native dependencies normally. Repository proof's initial
post-check confused apt's epoch filename with a pool filename; corrected
content-hash comparison passed. Raw failed logs remain on R730. No failed root
was selected for builds. The initial Python bytecode check hit a root-owned
cache directory; the check passed as the provisioning user without changing
permissions or services.

root-recipe-used.py matches the recorded004 recipe. The current reusable
builder additionally permits reuse of an already published SDK payload.
Recorded proof scripts are R730 qualification recipes; do not run them on the
laptop. Root/publication hashes, commands and exact acceptance limits are in
receipt files. This change does not upgrade GCC8 to GCC14 or claim desktop,
QEMU-system, Radeon, or physical A1222 acceptance.
