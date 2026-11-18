# QEMU patches

These are ordered, hash-pinned corrections to the locked QEMU (`profiles/qemu/amigaos-ati.json`). `scripts/build-qemu-ppc.py` applies them with `patch -p1` after extraction. `series` lists the order and `series.json` holds each patch's sha256.

| patch | issue | what |
|---|---|---|
| 0001-target-ppc-sync-spefscr-rounding-mode.patch | #3 | SPEFSCR[FRMC] now sets the SPE arithmetic rounding mode (`vec_status`) |
| 0002-linux-user-ppc-spe-fpexc-prctl.patch | #39 | linux-user answers `PR_GET_FPEXC`/`PR_SET_FPEXC` on SPE CPUs as the kernel does, so glibc's e500 `fegetenv`/`fesetenv` no longer load a stack word into SPEFSCR |

0002 changes only `linux-user/`. `scripts/build-qemu-ppc.py` builds `qemu-system-ppc`, where it compiles nothing; it matters for a `--target-list=ppc-linux-user` build such as the #27 dry runs. Evidence: `docs/builds/qemu-fpexc-prctl-20261118/`.

These are emulator corrections only. Physical A1222 results remain the acceptance gate for SPE behaviour.
