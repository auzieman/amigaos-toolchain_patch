# Reduced return-address regression — 2026-11-01

GitHub #9. Linux/SPE reference GCC8.5.0; same compiler/image/sysroot as libc003.
The exact initially executed source is `004-initial-probe.c`; input and artifact
hashes are in `004-initial-probe-hashes.txt`. The maintained version is
`bench/spe-return-address.c`, adding a sanity check on the returned address.

| Probe flags beyond base | Old libc | Debian libc003 |
| --- | --- | --- |
| plain | exit0 | exit0 |
| strong protector + exceptions | exit0 | exit0 |
| same + frame pointer | exit0 | exit0 |
| PIC + strong protector + exceptions | SIGSEGV139 | SIGSEGV139 |
| PIC + exceptions, no stack protector | exit0 | exit0 |
| PIC + strong protector + exceptions + frame pointer | SIGSEGV139 | SIGSEGV139 |

Base: `-O2 -g -mcpu=8548 -mabi=spe -mspe -mfloat-gprs=double
-mlong-double-128`, linked with `-ldl`, against reference sysroot. PIC means
`-fpic`; protection `-fstack-protector-strong`; frame-pointer flag
`-fno-omit-frame-pointer`. These are system-QEMU guest executions, not hardware.
See the two 004-return-address logs. Candidate invocation uses its explicit
loader and library path, keeping the installed baseline untouched. Exit139
happens before printing RETURN_ADDRESS, narrowing this probe to the compiler's
builtin implementation rather than the subsequent dl_iterate_phdr callback.

Disassembly of protected PIC caller loads SP+64 as a backchain, then
 dereferences that value+4. Its real saved LR is at SP+84. Plain/PIC-without-SSP
works. Explicit frame-pointer retention does not solve this case.

## Candidate compiler patch

`patches/gcc/bootstrap-8.5/0001-spe-pic-return-address.patch` is an independent
local experimental change, not a claimed upstream backport or modern GCC SPE
restoration. Inside rs6000_return_addr's PIC/full-frame branch, for count0 and
SPE ABI_V4 only, derive the saved-LR address from arg_pointer_rtx. The pinned
GCC8.5 source defines ARG_POINTER_CFA_OFFSET=0; its elimination offset is the
incoming stack pointer (total_size above the allocated frame). This avoids the
local-frame/backchain calculation while retaining strong stack protection.
All other target paths are untouched; they still require regression coverage.

Fresh build `gcc-unwind-002`, 4CPUs/6GiB, network-disabled on R730, builds C/C++
frontends and matching runtimes. Archive and patches are hash checked. Earlier
001 failed patch application because the hand-written hunk specified line1;
002 corrects the hunk position, applies with zero fuzz and has entered compile.
No accepted compiler, sysroot or libc artifacts were overwritten. A successful
build alone does not validate this candidate.

Next: run the full flag matrix with new compiler, compare assembly, then
rebuild Debian libc with the proven compiler and rerun dynamic ABI, C++ unwind,
thread/TLS and fenv checks. Keep #3 open. Do not disable hardening globally or
promote the new toolchain until the regression evidence is sufficient.
