# Libc004: original C++ unwind regression fixed in system QEMU

Fresh Debian glibc2.41-12+deb13u4+tabor1~stage2 build004 completed seven
artifacts with compiler8.5.0+tabor2. Normal dependency checking and Debian
packaging ran; patch006 requires the fixed compiler. Compiler correction
changes the actual dl_iterate_phdr backchain read from SP+64 to SP+0, while
retaining strong stack protection. See 007-libc-dl-iterate-disassembly.log.

Runtime libraries SHA256-match actual libc6 .deb payload and are read back
from private /home/tabor/glibc-stage2-004 after upload. The installed guest
baseline remains unchanged; library maps confirm candidate libc/libm.
The C probe's ELF PT_INTERP is checked to exclude static-probe mistakes.

- Original C++ binary with reference libgcc_s/libstdc++: long-double128,
  exception/RAII unwind, thread/TLS and atomic-u32 all PASS, exit0. Baseline
  also passes. Candidate003 previously exited139 before its exception check.
- Newly compiled C++ binary and matching new GCC runtimes: same four tests
  PASS with packaged libc004, exit0. Library map confirms both new runtimes.
- Dynamic C probe: float32/64, varargs, formatting, setjmp, signal, pthread/TLS
  and ucontext PASS. Fenv float/double directed rounding FAIL; mode selection,
  restore and exception bookkeeping PASS. Exit1 is retained as an open failure.

Evidence: 007-libc-build.json, 007-libc-package-proof.json, 007-qemu-runtime/
receipt.json and raw per-test logs; 007-new-cxx-tests.json plus build/loader logs.
Unwind issue #9 has met its original QEMU regression gate. Keep #3 open.
This does not establish full SPE ABI, physical A1222, final-feature libc, real
Debian installed root or Radeon/E acceptance. No USB write or runtime overwrite.

Desktop4 status/log/shell panes now follow current work and the current guest.
Log refresh reads at most24KB and displays10 lines of160 characters every4s,
preventing unbounded compiler output in the laptop terminal. noVNC remains
on the earlier E baseline until a newly assembled graphical image is ready.

Next: continue full-feature dependency/Essential bootstrap and configured
persistent disk root; isolate fenv emulator/runtime behavior without hiding
the failing check. Carry the fixed compiler through subsequent package builds.
