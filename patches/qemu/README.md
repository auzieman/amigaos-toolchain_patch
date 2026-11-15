# QEMU patches

These are ordered, hash-pinned corrections to the locked QEMU (`profiles/qemu/amigaos-ati.json`). `scripts/build-qemu-ppc.py` applies them with `patch -p1` after extraction. `series` lists the order and `series.json` holds each patch's sha256.

| patch | issue | what |
|---|---|---|
| 0001-target-ppc-sync-spefscr-rounding-mode.patch | #3 | SPEFSCR[FRMC] now sets the SPE arithmetic rounding mode (`vec_status`) |

These are emulator corrections only. Physical A1222 results remain the acceptance gate for SPE behaviour.
