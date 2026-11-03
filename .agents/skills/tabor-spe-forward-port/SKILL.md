---
name: tabor-spe-forward-port
description: Investigate or implement GCC/libgcc/glibc PowerPC SPE forward ports and validate the e500 userspace ABI.
---
For ongoing Debian package dependency closure or desktop builds, use
../tabor-debian-port/SKILL.md instead. Return to this workflow for a demonstrated
compiler/runtime or ABI defect; missing package dependencies are port-build
service work.

Read docs/task.md and docs/feasibility.md. Establish the Linux host/target tuple, endianness, float/long-double ABI and reference compiler/sysroot before selecting a modern target. Maintain component-specific ordered patches under patches/gcc, patches/glibc and patches/binutils with upstream origin and regression purpose. Review removed e500 sysdeps, compiler backend interfaces, libgcc helpers and signal/context state handling; reversing an old deletion is only a starting comparison. Bootstrap dependencies explicitly and keep host tools separate from target libraries. Require observable float/double/varargs, libm/fenv, setjmp, signals/ucontext, pthread/TLS, atomics and C++ unwinding results before claiming restored support. Preserve generic PowerPC regression coverage. AmigaOS SDK integration needs its own runtime/ABI contract; do not substitute Linux glibc for an AmigaOS runtime by assumption. Defer Mesa/GPU integration until the selected userspace ABI passes these checks.
