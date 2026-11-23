# Kernel 021 (2026-11-23): 016 + Derf's 0037/0038, quiet amdgpu traces, desktop config

## Source

The running kernel's tree, `work/e2e-usb-20261113-016/source` on the R730, with:

- 0037, amdgpu dce_v11 host-byte-order framebuffers on big-endian (Derf, #35)
- 0038, exec starts with a defined SPEFSCR (Derf, #48/#41)
- 0039, `make-0039.py`: the 20 bring-up `INIT_TRACE`/`PWR_TRACE`/`SMU_DIAG`/`SMU_CALIB`
  prints go from info to debug level. On 016 they made 148,681 kernel log lines in a 3.8-day
  boot, with kmsg overruns, all stored on the root USB stick. With `CONFIG_DYNAMIC_DEBUG`
  they can be turned back on, e.g. `amdgpu.dyndbg=+p`.

All three applied without fuzz. Derf's 017-020 trees are not on the R730. 0037 and 0038 apply
to 016 directly.

## Config and build

016's config (sha256 `71738b3c...`, matching the 016 receipt) with the changes in
`build-021.sh` and `config-016-to-021.diff`: LOCALVERSION `-tabor-e2e-021`, NR_CPUS 2,
PREEMPT_VOLUNTARY, HZ 1000, DYNAMIC_DEBUG, SND_HDA_INTEL/SND_HDA_CODEC_HDMI as modules.
The board list is not trimmed in 021, so a regression can be attributed.

Built in 016's tools image `sha256:2781e118...` (Debian powerpc-linux-gnu-gcc 14.2.0, as 016),
4 CPUs, no network. `make` exit 0, one warning (`gfx_v8_0.c:884`, as in 019/020).

| File | sha256 |
|---|---|
| `vmlinux` | `a6cd3c09b0783b2bdff5d4b93723dec8db469fe5b1897df3da2179a4916793e3` |
| `uImage` | `c714afa7b8f0d413e6d64ceeba25727cf4dc5ba53b4e2d9c6306fc0c5e1bc696` |
| `tabor.dtb` | `e97a43fcbfee804d7fece5c9010f188c73c5bdaa63d3213f17deda77cd16726d` (identical to 016-020) |
| `stage-021.tar` | `51534c72c49f300ffe121b8e719c3f59450751d0403c826896ee442d4c2a46f8` |

48 modules (016: 43, plus HDA).

## Boot scripts

`make-boot-cmds.py` writes a `boot.scr` that does not depend on USB enumeration order. The
firmware's saved command sources `/boot.scr` from `usb 0:1`, which is the PNY when the PNY
enumerates first. So the same script is on both sticks. It looks for `/tabor.id` (an 8.3 name
that only the SanDisk has) on usb 0-3 and boots from that stick: 021 with `panic=0`, falling
back to 016 if 021's files do not load. The search is unrolled `if fatload ...` blocks,
because the board has only run if/fatload/iminfo/setenv/bootm before. The marker loads at the
kernel address, where the proven script already loads, so it cannot overwrite the running
script.

Checked under U-Boot 2025.01 hush (`qemu-ppce500`, Debian u-boot-qemu). That build has no
filesystem commands, so each `fatload` was replaced by a `test` with the simulated result:
- PNY as usb 0, SanDisk as usb 1 with only 016 files: usb 0 skipped, 021 missing, falls
  back to 016.
- SanDisk as usb 0 with 021: `iminfo` passes on a real uImage, `bootm` reached with
  `panic=0` bootargs.

The firmware's own USB scan happens before the script runs. If the firmware hangs while
scanning the PNY, no script can help: insert the PNY after boot (`/srv/build` is `nofail`).

## Install (`install-021.sh`, 2026-11-23)

The install adds files only. On the SanDisk FAT: `/boot/e2e-021/{uImage,tabor.dtb}`,
`tabor.id`, `boot.scr`, `boot-016.scr`, with the old scripts kept as `*.pre-021`. On the PNY
FAT: the same two scripts, without the marker. It also installs
`/lib/modules/6.12.113-tabor-e2e-021` and `/etc/modprobe.d/tabor-021-hda-hold.conf`, which
blacklists snd_hda_intel until it is tested by hand. 016's kernel, DTB and modules are
untouched.

Rollback at the U-Boot prompt: `fatload usb 0:1 0x09000000 /boot-016.scr; source 0x09000000`
(use `usb 1:1` if the PNY is usb 0). From Linux: copy `boot.scr.pre-021` over `boot.scr` on
the SanDisk FAT.
