# GCC14 runtime continuation

GCC14 static libgcc passed (runtime attempt003). The fresh glibc diagnostic
uses the existing patched Debian2.41-12+deb13u4 source read-only and UAPI/sysroot
read-only, writing only a new glibc-gcc14-001 build directory under the GCC14
candidate workspace. Source preparation provenance is retained in the previous
debian-glibc-402 receipt. This is bootstrap qualification, not a Debian package
build or accepted replacement SDK. No runtime is installed by this recipe.

R730 container: tabor-glibc-gcc14-001, network none,4 CPUs/6GiB.
Image: sha256:2781e11839beffa351f8c411d71b7e2bd1ae0336d24c60b407778c3350dd9da0.
Configure completed, selected the restored e500 sysdeps, accepted long-double128
and began make. Result/build logs live in the new directory; final compilation
and ABI acceptance remain pending. The script beside this file records the
actual build commands. Host archiver/binutils remain native tools.

After runtime acceptance: package-managed root, existing harness, X/E and
scripts/visual-gl-smoke.sh. A software-rendered gears window is separate from
physical Radeon acceleration. Boot media remains unchanged.

Follow-up: first build reached libc/loader object assembly, then failed at
Makerules:620 because OBJCOPY was omitted from the bootstrap recipe and native
x86 objcopy rejected PPC libc_pic.os. The recipe now explicitly selects target
objcopy/strip, matching the other binutils. Bounded container
tabor-glibc-gcc14-002 resumes the same output with make overrides; logs
build-002.log/result-002.exit preserve this attempt separately. No driver or
libc source patch was needed for this tool-selection failure.

Glibc make attempt002 completed with exit0 (2026-11-07). Both libc.so.6 and
the target loader were produced. A separate staging container installs into
/work/runtime-stage-001 only, then compiles bench/spe-abi-smoke.c using GCC14
and the fresh glibc startup files/libraries. No baseline root or USB is altered.
Container tabor-gcc14-runtime-stage-001 is bounded4 CPUs/6GiB, network none.
QEMU execution must explicitly invoke the new loader and its library directory;
compilation/install success alone is not ABI acceptance.

Runtime result: new GCC14-linked dynamic probe explicitly executed with the
new GCC14-built glibc loader/libc/libm under QEMU e500v2. Seven of nine top-level
ABI checks pass: float32, float64, formatting, setjmp, signal, pthread_tls and
ucontext. Varargs and fenv fail at both O2 and O0; exit1 is preserved. Raw logs
include executable/library SHA256. This runtime is not accepted for the new
image. Staging completed after MAKEINFO=: addressed DFSG-omitted manual files;
headerless compiler probe requires explicit read-only Linux UAPI include path.
Next: isolate compiler va_list/call lowering versus header ABI, comparing the
existing libc-free passing fixture and GCC8 reference; keep fenv rounding as a
separate existing gate. No blanket package/driver workaround or USB update.

Compiler experiment: RTL for the failing direct double return selected
*frob_df_di with a memory source; emitted evmergelo used its address register
as floating data rather than loading the spilled result. Restricting the
SPE64/DITI subreg conversion to register operands forces valid reloads. Compiler
all-gcc rebuild passed. Recompiled original ABI probe now passes varargs at
O2 and O0, leaving fenv as the only failing top-level check (8/9 pass).
Experiment patch and raw logs are retained here, not yet promoted to the
ordered16-patch candidate series. Remote modern source/compiler include this
experiment; previous compiler hashes no longer describe that executable.
Existing glibc/libgcc were not rebuilt with this change. Next: minimize/qualify
conversion regression, integrate reviewed patch and replay source, rerun
freestanding/vector checks and rebuild runtimes before SDK acceptance.

## Native GCC14/glibc milestone — 2026-11-07

The original SPE C ABI probe, compiled with GCC14 plus candidate patch17,
passes all9 top-level checks on the physical A1222, including varargs and
floating-point rounding, exit0 and kernel taint0. Fresh GCC14-built glibc2.41
loader/libc/libm were copied to a private /tmp directory and invoked explicitly;
no system libraries, kernel, USB boot files or accepted SDK were replaced.
Exact uploaded SHA256 and output: builds/gcc14-runtime-20261107/hardware-runtime-001.json.
QEMU user-mode still fails rounding with the same candidate executable/libraries;
do not weaken native libc semantics to accommodate that emulator result.

Patch17 restricts SPE subreg conversions to register operands, avoiding a
miscompiled spilled double-return conversion. Original ABI test passes varargs
at O0/O2 in QEMU. This checkpoint used libraries built before patch17: a fresh
bounded regression/libgcc/glibc rebuild is now launched on the R730 as
`tabor-gcc14-runtime-rebuild-002`. Full C++/unwinding/long-double and broader
cross-version/generic PPC regression acceptance, Debian packages and image
assembly remain open. Native Trixie workstation remains the end goal.

The corrected compiler passes the existing20 automatic freestanding/vector
qualification checks. Patch17 also replays cleanly on the previously
reconstructed16-patch source; its spe.md matches the compiled candidate.
