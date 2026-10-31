# R730 fenv diagnostic before the larger desktop build

The aggregate floating-environment failure is now split into independent
checks without relaxing acceptance. Fresh R730 `abi-live-003` recompiles the
probe with the canonical SPE/long-double-128 flags and runs it on kernel
`qemu-live-005`. [Receipt](builds/r730-fenv-20261031/receipt.json) and
[raw output](builds/r730-fenv-20261031/serial.log) retain the failed result.

| Check | QEMU result |
|---|---|
| Set/read upward and downward modes | PASS |
| Float addition under directed rounding | FAIL |
| Double addition under directed rounding | FAIL |
| Restore saved rounding mode | PASS |
| Clear/raise/test/clear exception APIs | PASS |

Upward mode reads back as 2 with SPEFSCR `0000003e`; downward reads back as 3
with SPEFSCR `0000003f`. Both additions nevertheless return 1.0 for the halfway
operand. The original eight other C ABI checks continue to pass. The exception
check covers the tested library APIs, not every arithmetic trap or signal case.

A bounded review of the retained QEMU 11.1.3 source finds that
`spr_write_spefscr` in `target/ppc/translate.c` stores the register, while SPE
addition in `target/ppc/fpu_helper.c` uses `vec_status`. The write callback does
not update that arithmetic rounding state. The same structure is present in
upstream [v10.0.0 translation](https://github.com/qemu/qemu/blob/v10.0.0/target/ppc/translate.c)
and [floating helpers](https://github.com/qemu/qemu/blob/v10.0.0/target/ppc/fpu_helper.c).
Local reviewed file hashes are retained in
[source-review.json](builds/r730-fenv-20261031/source-review.json).

This supports an emulator-state synchronization hypothesis. It is not a tested
QEMU correction and does not prove the native A1222 libc passes. Keep the
existing USB image and failure evidence unchanged. A bounded next experiment
is to replay the diagnostic on the real board, or test a separately pinned QEMU
rounding-state correction with the same unmodified probe. Mesa/GPU integration
remains behind the ABI gate; building the missing reference C++ runtime and its
unwind/thread/atomic probes is independent prerequisite work.
