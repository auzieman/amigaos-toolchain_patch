# QEMU: apply SPEFSCR[FRMC] to SPE arithmetic rounding (#3) — 2026-11-15

## Defect

`bench/spe-abi-smoke.c` fails its directed-rounding checks under QEMU but passes on the physical A1222. This was confirmed again with the GCC14 candidate 0001-0022 toolchain:

| | FENV float_round / double_round | FENV_DETAIL |
|---|---|---|
| qemu-ppc 11.1.3, pristine | FAIL / FAIL | `up=0x1p+0 float_up=0x1p+0` |
| physical A1222 | PASS / PASS | `up=0x1.0000000000001p+0 float_up=0x1.000002p+0` |

## Cause

As `docs/fenv-rounding.md` suspected: in QEMU 11.1.3 `spr_write_spefscr` (`target/ppc/translate.c`) only stores `env->spe_fscr`, while the SPE helpers (`efs*`, `efd*`, `evfs*` in `fpu_helper.c`) round using `env->vec_status`. Nothing ever copied SPEFSCR[FRMC] into `vec_status`, so SPE arithmetic always rounded to nearest. The other writers of `spe_fscr` had the same gap: linux-user sigreturn, gdbstub and migration post-load.

## Fix

`patches/qemu/0001-target-ppc-sync-spefscr-rounding-mode.patch` follows the existing `ppc_store_fpscr` pattern:
- It adds `ppc_store_spefscr(env, val)`, which stores SPEFSCR and sets the `vec_status` rounding mode from FRMC (0 nearest, 1 toward zero, 2 toward +inf, 3 toward -inf).
- `mtspr SPEFSCR` uses it through a new TCG helper `helper_store_spefscr`, and so do linux-user sigreturn, gdbstub and migration.

`patches/qemu/series` and `series.json` pin it by hash. `scripts/build-qemu-ppc.py` checks the hashes and applies the series after extraction, recording the patches in its receipt.

`scripts/check-qemu-spe-rounding.py` builds the unmodified `bench/spe-abi-smoke.c` with a given SPE compiler, runs it under a given `qemu-ppc` (linux-user, `-cpu e500v2`), and requires both directed-rounding checks to pass.

## Validation

QEMU 11.1.3 from the pinned archive (`sha256 5a8289c7…`). `qemu-ppc` (ppc-linux-user) was built from the pristine tree and from the patched tree.
- `check-qemu-spe-rounding.py` fails on the pristine build (`up=0x1p+0`) and passes on the patched one. The patched values, `up=0x1.0000000000001p+0 down=0x1p+0 float_up=0x1.000002p+0`, are identical to the physical A1222.
- `patch -p1 --dry-run` applies cleanly to a pristine 11.1.3 tree.
- `qemu-system-ppc` (ppc-softmmu, with the configure flags of `build-qemu-ppc.py`) builds with the patch and lists `ppce500`.
- Regression: every SPE GCC 14.2 torture binary (execute + ieee, 0001-0022 toolchain, static; -O0/-O2/-O3, 1719/1720/1720) was run under both builds. All pass under the pristine and the patched `qemu-ppc` alike, with no per-test differences, matching the physical A1222 results.

Limits:
- System-mode run-time rounding was not exercised here; it needs the rescue kernel and disk. The `mtspr` path is the same code in both modes.
- `build-qemu-ppc.py` itself cannot currently extract the 11.1.3 archive on Python 3.13 (#37). That is independent of this patch.
