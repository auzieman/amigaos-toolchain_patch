# Tabor machine-match kernel rebuild — 2026-11-05

Tracks issue https://github.com/auzieman/amigaos-toolchain_patch/issues/26.
Rebuild is a controlled correction of the actual USB kernel, not an upgrade of
the frozen workstation/toolchain baseline. Linux source remains 6.12.113-1 and
build-image identity remains sha256:2781e11839beffa351f8c411d71b7e2bd1ae0336d24c60b407778c3350dd9da0.
The kernel is freestanding and uses the retained powerpc-linux-gnu build tools;
no GCC14 userspace SPE-restoration acceptance is inferred.

Artifact provenance correction: board-boot-001 and board-package-input-001
refer to work/tabor-live-001, kernel ELF SHA256
185e5d71519f852749381ab4a25768f70dda80fcf116146587e8ec121659cd5c,
configuration SHA256
4be2739e4620d8ae44b1b9d8788aee81495b23a352bdba135913a0fab6aaa498.
The later tabor-live-002 configuration was not deployed to the USB. Previous
source identity auditing applies to both (same original board patch); the
layered-image builder checked later config hardware capabilities, not actual
ELF/config lineage. This rebuild uses the exact original 001 configuration.

Fresh run work/tabor-match-20261105-002 re-extracts cached, hash-verified Debian
source and applies ordered patches 0001 and 0002. --kernel-config copies the
retained configuration, runs olddefconfig, and refuses any byte/hash change.
The actual post-olddefconfig hash matches the retained original. Source,
cache, build image and original kernel outputs remain separate and preserved.
Build runs on R730 with four compiler jobs, four CPUs, 6GiB and no network.

Infrastructure evidence: first launch used the image's shell entrypoint and
failed before source/build; corrected with explicit Python entrypoint. A
subsequent run using the later 002 configuration was stopped before completion
when the actual USB provenance was resolved; the accepted build uses 001.
No outputs from those preliminary runs replace shipped artifacts.

Packaging must pass the machine-compatible guard with exact rebuilt tabor.c
and DTB. USB update is restricted to the exact SanDisk serial and /boot/uImage,
with previous kernel backed up on host, staged-file hash, synced readback and
unchanged DTB/script/README checks. Root partition is never mounted or opened
for writing. Hardware acceptance stays open until actual Linux/SSH output.

Build completed successfully: vmlinux, modules and DTBs. Exact configuration hash retained; DTB hash unchanged; machine guard passes for varisys,TABOR. ELF physical extent remains 0x256d38c; packaging CRCs and decompression passed. Kernel SHA256 abcbd321c48ce7f465487637fb6638100756e96a4ec9b74f5d3c7e47c894601a; uImage SHA256 90fe78857d06b66186c3a9698803015ed63907e15ccd0f1620f74376ea866146. No physical boot claim.

USB update completed: exact SanDisk serial verified, previous uImage backed up locally, corrected file written and hashed, then boot partition unmounted/remounted read-only and hash verified again. DTB/script/README hashes unchanged; root partition not written. Device unmounted and powered off. Initial updater preflight refused a flat lsblk JSON tree before mounting/writing; fixed by explicitly requesting --tree and NAME. No media write occurred in that refused attempt. Hardware retry is pending.
