# A1222 GPU BAR0 above PCI 4 GB (#34) — experiment, not adopted — 2026-11-16

## Question

amdgpu cannot resize the RX 550's BAR0 to 4 GB (`Problem resizing BAR0 (-22)`), so only 256 MB of VRAM is CPU-visible. Can a larger window be given to the GPU's PCIe controller (`pcie@fffe0a000`, `pci1`, PCI domain 0001)?

## Platform facts (read-only, kernel 017)

- **CPU side.** The e500v2 core is 32-bit with 36-bit physical addressing (`CONFIG_PHYS_64BIT=y`). The GPU's existing window is already a 36-bit CPU address: CPU `0xc_4000_0000` -> PCI `0xe000_0000`, 512 MB.
- **LAWs** (U-Boot): LAW1 `0xc_4000_0000` 512 MB target 0x02 (PCI Express 1), LAW2 `0xf_ffc2_0000` 64 KB (I/O), LAW11 DDR. LAW3-LAW10 are free. Linux does not program LAWs.
- **Inbound ATMU.** The only enabled window, PIW3, maps PCI `0x0-0xffff_ffff` onto RAM (`mem=3500M`) for device DMA. The GPU's outbound window already uses the top 512 MB of that 32-bit PCI space, so a larger BAR in 32-bit PCI space would need a smaller DMA window. Without an IOMMU that loses DMA to most of RAM.

A 4 GB BAR0 therefore has to live at a PCI address above 4 GB.

## Patch tried (0036, not in any series)

`0036-tabor-pcie-law-and-gpu-prefetch-window.patch` against the kernel017 tree (`build-env` `make-0036.sh` / `build-018.sh`):
- **`tabor.c`.** Before PCI probe it opens a free LAW for every host-bridge `ranges` window that no enabled LAW covers. It reuses the target ID of the LAW that already routes the same controller. The first build used `is_power_of_2()`, which takes `unsigned long` (32-bit), so it skipped the 8 GB window; the archived patch has the u64-safe test.
- **`tabor-a1222.dts`.** `pci1` gains `<0x43000000 0x1 0x0  0x8 0x0  0x2 0x0>`, a 64-bit prefetchable window from CPU `0x8_0000_0000` to PCI `0x1_0000_0000`, 8 GB.

## Trials

Both ran on power-cycled boots with the root read-only.

1. **Kernel 018, amdgpu** (`trial1-018-amdgpu.txt`).
   - Linux accepted the window (`root bus resource [mem 0x800000000-0x9ffffffff 64bit pref]`, outbound ATMU 2 programmed). LAW3 was written by hand (`0x00800000` / `0x80200020`) because of the bug above.
   - `modprobe amdgpu polaris11_le_user_ib=1`: the resize was still -22. The fallback moved BAR0/BAR2 to `0x8_0000_0000`, then `Machine check ... Bus - Read Data Bus Error`, SIGBUS, taint 144.
   - Afterwards every register was as intended: LAW3, ATMU 2, the root port's prefetchable window `0x1_0000_0000-0x2_ffff_ffff`, GPU BAR0 = `0x1_0000_0000`, no inbound overlap.
2. **Kernel 017, no driver loaded** (`trial2-017-devmem.txt`).
   - A baseline read of GPU BAR0 at CPU `0xc_4000_0000` returned `0x55AD55AD`, U-Boot's framebuffer pattern.
   - By hand: LAW3 (8 GB, target 0x02); outbound ATMU 3 (`potar 0x00100000 powbar 0x00800000 powar 0x80044020`); the root port's 64-bit prefetchable window `0x1_0000_0000-0x1_0fff_ffff`; GPU BAR0 -> `0x1_0000_0000` with memory decode off while changing it. All read back correctly.
   - A single `devmem 0x800000000 32` (PCI `0x1_0000_0000`) gave `Machine check ... MCSR=10008 Bus - Read Data Bus Error`, taint 144.

## Conclusion

On this A1222 the P1022 PCIe controller does not complete outbound reads at PCI addresses above 4 GB, even with no driver involved and with every window programmed and read back. The 32-bit PCI space is already split between the inbound DMA window and the 512 MB outbound window. So a 4 GB (or any larger-than-512 MB) CPU-visible VRAM window is not achievable with the current platform setup. The driver keeps 256 MB visible, and radeonsi keeps using CP-DMA shader uploads, which is correct with patch 0035.

Not explored: P1022 errata or reference-manual conditions for 64-bit outbound PCIe addressing. If a documented condition exists, `0036` and the trial method here are the starting point. No firmware environment, U-Boot or AmigaOS setting was changed. The stick's default boot script stayed on 016.
