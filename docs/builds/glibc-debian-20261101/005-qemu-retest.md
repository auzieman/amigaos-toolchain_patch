# Compiler candidate002 QEMU retest

The compiler and matching C++ runtime rebuilt successfully (005-gcc-receipt).
Tests compiled using that installation (005-probe-build), executed in existing
software-e010 system-QEMU guest with baseline and explicit Debian003 loader.
Four modes pass both runtimes. PIC+strong-protector and same+frame-pointer
segfault139 both runtimes. See 005-patched-qemu-matrix.log. Guest sha256sum
command was unavailable; those diagnostics are not validation failures of the
probe itself, and no guest hash verification is claimed. Build artifacts have
recorded server hashes. Existing installed runtime was not overwritten.

The patch changed the inactive regular rs6000 backend. The active Makefile
selects config/powerpcspe/powerpcspe.c; its return-address helper still uses
the local frame to read the backchain, whereas the regular backend has a
depth-zero SP correction. Candidate0002 applies that correction to the active
backend. Candidate0001 remains failed history, excluded from active series.
Fresh gcc-unwind-003 is compiling; no pass or fixed-libc claim yet.
