# #38: -fzero-call-used-regs on SPE (GCC14 candidate 0023) — 2026-11-16

## Failure

Debian openssl 3.5.7 compiles with `-fzero-call-used-regs=used-gpr`. The qualified GCC14 SPE SDK (`tabor-spe-toolchain 14.2.0+tabor1`, candidate 0001-0022) failed on every function compiled with it (`openssl-tabor1-ice.txt`):

```
during RTL pass: zero_call_used_regs
internal compiler error: in change_address_1, at emit-rtl.cc:2299
  emit_move_insn <- default_zero_call_used_regs
```

It failed at -O0 and -O2, and with `used-gpr`, `used`, `all-gpr` and `all`. Debian's hard-float `powerpc-linux-gnu-gcc-14` compiles the same code, and so does the SPE compiler with SPE turned off.

## Cause

The powerpcspe backend has no `TARGET_ZERO_CALL_USED_REGS` hook, so the generic `default_zero_call_used_regs` zeroes each register in its raw mode. Under SPE the raw mode of a GPR is a 64-bit mode, so after reload the code moves a 64-bit constant zero into each GPR. That move goes through the constant pool and asserts.

## Fix: `patches/gcc/gcc14-spe-candidate/0023-spe-zero-call-used-regs-hook.patch`

`rs6000_zero_call_used_regs`, active under `TARGET_SPE`, does two things:

- **GPRs:** it zeroes each requested GPR as a V2SImode zero vector, the zero alternative of `*movv2si_internal`. The result is `evxor rN,rN,rN`, which clears both 32-bit halves.
- **CR fields, CTR, LR:** it zeroes them directly where a move from zero is a valid insn. Otherwise it copies a zeroed GPR (`mtctr`, `mtcrf`), as the generic code does.

SPE_ACC and SPEFSCR are fixed registers, so they are never requested, and the rounding mode is untouched. Without `TARGET_SPE` the default is used.

## Evidence

- `scripts/check-spe-zero-call-used-regs.py` (new) compiles four functions at -O0/-O2 for all seven modes. It requires every compile to succeed and every `used-gpr` function to clear its call-clobbered GPRs with `evxor` without touching r3/r4.
  - tabor1: 14 of 14 compiles ICE (`check-tabor1.json`).
  - tabor2: pass (`check-tabor2.json`).
- **Runtime:** `run.c` (64-bit integer, double, loop and struct-return functions) was built with every valid mode at -O0/-O1/-O2/-O3/-Os and run under qemu e500v2. All 35 builds give the reference output.
- **Rounding:** `fe.c` sets FE_UPWARD, divides, restores FE_TONEAREST and divides again. It was built with tabor2 under `skip`, `used`, `used-gpr` and `all` and run under the #3-patched qemu-ppc (`fe-rounding-patched-qemu.txt`). Each run gives `0x1.5555555555556p-2` then `0x1.5555555555555p-2` and exits 0, so the zeroing leaves SPEFSCR's rounding mode intact. Stock qemu-user ignores the rounding mode (#3) and cannot show this.
- **No other code change:** the GCC torture suites were compiled with tabor1 and tabor2 at -O0/-O2/-O3, without the flag, in a container with the target headers. The assembly is identical for all 4641 execute compiles (`torture-asm-tabor1-vs-tabor2-with-headers.txt`) and all 204 ieee compiles (`torture-ieee-asm-tabor1-vs-tabor2.txt`). The other 327 execute compiles fail with both compilers alike. The earlier run without headers covered 4296 compiles (`torture-asm-tabor1-vs-tabor2.txt`). The libgcc_s, libstdc++ and libatomic code disassembles identically, so the `14.2.0+tabor1` runtime packages are kept.
- `check-gcc14-spe-candidate.py` passes 22/22 on tabor1 and on tabor2 with `--qemu` (the #3-patched qemu-ppc), and 20/20 without it, and so do the four existing `check-spe-*` scripts (`*-tabor2.json`).
- **openssl 3.5.7** builds through `run-sbuild-package.py` with tabor2, with Debian's `-fzero-call-used-regs=used-gpr` kept (`sbuild-openssl-gcc14-003.receipt.json`). libcrypto has 54,836 `evxor` clears.
  - Under qemu e500v2 its sha256, sha3-512, blake2b512 and md5 digests match the host's.
  - Data it encrypts with aes-256-cbc decrypts on the host, and host chacha20 output decrypts on SPE.
  - ECDSA P-256 and ML-DSA-44 signatures it makes verify with the host openssl.

## SDK

`scripts/build-gcc14-spe-sdk.sh`, run package-managed (`PREFIX=/usr/lib/tabor-spe-toolchain INSTALLED_SYSROOT=/ MULTIARCH=1`) with 0001-0023, then `package-gcc14-spe-host-toolchain.py --version 14.2.0+tabor2`, produces `tabor-spe-toolchain_14.2.0+tabor2_amd64.deb`, sha256 `24b4f16c4649d355…` (`tabor-spe-toolchain-receipt.json`). `profiles/compiler-policy.json` is re-pinned to it, and tabor1 is recorded as superseded. `crossbuild-essential-powerpcspe 1.0+spe9` selects it.

Not checked here: `patches/openssl/0001` probes the option by compiling `/dev/null`. That probe would pass even on a compiler that ICEs on real functions.
