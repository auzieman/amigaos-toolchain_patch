# build-qemu-ppc.py on Python 3.13 (#37) — 2026-11-15

## Defect

`scripts/build-qemu-ppc.py` extracts the pinned `qemu-11.1.3.tar.xz` with `tarfile.extractall(..., filter='data')`. On Debian trixie (Python 3.13.5) this aborted before anything was built:

```
tarfile.AbsoluteLinkError: 'qemu-11.1.3/roms/edk2/EmulatorPkg/Unix/Host/X11IncludeHack' is a link to an absolute path
```

## Change

- **Extraction filter:** the script still applies `tarfile.data_filter` to every member. A member under `qemu-<version>/roms/` that the filter rejects is skipped and recorded in the receipt (`extraction_skipped`, with member and reason). `roms/` holds firmware sources that a ppc-softmmu build never uses. A rejection anywhere else still aborts.
- **Docstring:** it now lists the Debian host packages. `python3-setuptools` and `python3-wheel` are needed because configure runs QEMU's `mkvenv` offline (`--disable-download`). Without them configure fails with "Could not provide build dependency 'qemu.qmp'".

## Validation

Fresh `--work`, the pinned archive (`sha256 5a8289c7…`), Debian trixie with those packages:
- receipt `status: compiled`, `version: QEMU emulator version 11.1.3`;
- `patches: [patches/qemu/0001-target-ppc-sync-spefscr-rounding-mode.patch]`, so the #3 series was applied;
- `extraction_skipped: [qemu-11.1.3/roms/edk2/EmulatorPkg/Unix/Host/X11IncludeHack (AbsoluteLinkError)]`, the only member skipped;
- dtc fetched at the locked revision `b6910bec…`;
- `qemu-system-ppc` built.

The archive pin and the configure flags are unchanged.
