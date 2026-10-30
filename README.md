# Tabor SPE toolchain — private development

Modernize the A1222/Tabor e500v2/SPE toolchain and Linux userspace, with a
separate future AmigaOS SDK integration track. Local private repository only;
no remote or Hyperion source imported. Collaboration interest was reported by
the user; no access, endorsement or SDK compatibility is inferred.

## First deliverable

Reproduce the vendor Linux 5.4-rc3 baseline and boot format through the existing
`tabor-linux-forge` board workbench, then forward-port its small board/DTS/audio
series to a pinned modern kernel. A kernel build uses a freestanding PowerPC
compiler and binutils; it does not validate a target glibc or SPE userspace ABI.
Do not make a modern glibc a prerequisite for this first kernel artifact.

## Toolchain deliverable

Maintain separate versioned patch series for binutils, GCC/libgcc/libstdc++ and
glibc. GCC's SPE target was removed in GCC 9; glibc removed its SPE support in
2.30. Establish a historical SPE reference compiler/runtime first, then select
and pin the modern port target after auditing the removal and supplied patches.
A simple reverse-apply of the removal is an investigation aid, not an accepted
forward-port. Generic PowerPC soft-float and hard-float SPE are separate ABI
choices, not interchangeable compiler switches.

Bootstrap order: binutils → bootstrap GCC → Linux UAPI headers → libc bootstrap /
libgcc stages as required → complete glibc → final GCC/C++ runtime → ABI tests.
Record the exact bootstrap recipe and sysroot; host glibc and target glibc are
independent. Keep kernel-only compiler acceptance separate from userspace.

## Acceptance sequence

1. Vendor baseline patch/config/DTS provenance and unchanged build evidence.
2. Pinned modern kernel build, correct board DTB/boot wrapper, then serial boot
   on the A1222. QEMU e500 is useful but does not emulate the complete board.
3. Modern SPE compiler/runtime: ELF attributes and instructions; float/double,
   varargs, libm/fenv, setjmp/longjmp, signals/ucontext, pthread/TLS, atomics,
   exceptions/unwinding and C++ interoperability against a reference sysroot.
4. Linux graphics: kernel DRM/firmware plus userspace libdrm/Mesa/EGL/OpenGL
   built for the selected ABI. Software rendering and real GPU rendering are
   separate checks; GPU model and LLVM/JIT requirements remain to establish.
5. AmigaOS SDK: determine host/target, object/ABI/runtime requirements and supplied
   source/licenses. Linux glibc is not automatically an AmigaOS C runtime. No
   AmigaOS kernel build acceptance is possible before source/tool contracts exist.

See docs/feasibility.md, docs/intake.json and docs/task.md. Existing board source
remains owned by the separate Tabor workbench. This project stores references
and hashes, not a duplicate SDK, disk image or vendor code dump.
