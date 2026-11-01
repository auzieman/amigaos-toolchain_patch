# Active SPE backend fix: QEMU acceptance

Fresh GCC8.5 build gcc-unwind-003 completed frontends and matching C/C++
runtimes. 006-gcc-receipt.json retains source, patch and install-tree hashes;
006-backend-selection.log confirms powerpcspe, not regular rs6000.

All18 tests pass in existing software-e010 system-QEMU: nine compiler flag
modes against both installed baseline libc and explicit Debian003 loader/libc.
Includes formerly crashing protected PIC, frame pointers, uppercase -fPIC,
-fstack-protector-all and unoptimized code. Maintained probe checks returned
address range and dl_iterate_phdr callback. Each uploaded binary is read back
and SHA256 checked, not dependent on a guest sha256sum utility.

Raw commands, flags, frontend/binary hashes and per-case stdout/exit codes are
in 006-qemu-matrix/receipt.json. This proves the reduced compiler regression
is fixed in QEMU. Debian003 libc still contains its old broken generated code;
it must be freshly rebuilt and pass original C++ unwinding before #9 closes.
Fenv #3 and physical A1222 proof remain separate gates.

Compiler packaged as native-host tabor-spe-toolchain8.5.0+tabor2. The libc
source dependency now requires that version; image update uses normal dpkg
configuration in a separate pinned build image. No global hardening disable.
