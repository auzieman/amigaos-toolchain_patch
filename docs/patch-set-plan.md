# SPE and A-EON forward-port patch sets

Objective: recover the required legacy e500v2/SPE implementation and carry it
forward to selected newer compiler, glibc and Linux revisions, including the
necessary A-EON/Tabor board changes. Generic PowerPC support is not presumed
removed. First compare each target's existing implementation; restore only
missing support or adapt demonstrated interface changes.

## Separate series

| Series | Source evidence | Acceptance |
| --- | --- | --- |
| GCC / libgcc | Downloaded NXP SPE compiler, last supported upstream implementation and removal history | Correct instruction generation, calling conventions, runtime helpers and regressions |
| glibc | Historical NXP EGLIBC, last upstream SPE sysdeps and removal commit | Configure/sysdeps selection, fenv/libm, saved SPE state, signals/context, threads/TLS and ABI interoperability |
| Linux CPU / SPE | Legacy and target arch/powerpc CPU definitions, exceptions and context-switch paths | Retained/restored e500v2 and SPE configuration, compilation and execution tests; no duplicate support |
| A-EON / Tabor | Existing A-EON 5.4-rc3 board/audio patch, DTS and config | Reviewed Tabor platform/DTS/audio deltas, correct dependencies and boot handoff |
| Binutils | Chosen compiler/ABI requirements versus existing assembler/linker support | Add patches only for a demonstrated gap; verify target ELF/instruction handling |

The vendor patch contains changes for boards beyond Tabor. Review/split those
before carrying it forward; preserve the untouched historical baseline. Board
support is not a replacement for the compiler or libc ABI restoration.

## First implementation slice

1. Pin exact modern target revisions and retain their unmodified baseline checks.
2. Compare last supported upstream GCC/glibc SPE code with the vendor references;
   identify vendor-only changes independently of upstream removals.
3. Map target kernel CPU/SPE paths and split the existing vendor board patch
   into justified Tabor pieces. Keep unrelated boards deferred.
4. Implement one component change at a time, with a regression purpose and
   upstream origin recorded for every patch. Keep failed experiments separate
   from accepted series; do not weaken tests to obtain a successful build.
5. Verify ordered application against fresh exact revisions, then compile and
   test through the constrained BKC lab-edge lane. Save patch/config/toolchain
   and artifact hashes. A build result is separate from real A1222 boot or
   userspace ABI acceptance.

No restoration patch is accepted merely because an old deletion can be reversed.
There is no selected modern target or completed restoration patch yet. Minimal
USB boot work can proceed on its kernel-only lane while userspace restoration
is evaluated, with the rescue userspace ABI explicitly recorded.
