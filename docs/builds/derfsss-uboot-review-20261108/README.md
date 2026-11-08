# Derfsss A1222 firmware source review — 2026-11-08

Pinned repository: https://github.com/derfsss/u-boot_A1222/tree/9bfbc801b8ebec66bb4860fe0e8d15db9d786626
Read six files: board/aeon/tabor/{tabor.c,video.c}, include/configs/tabor.h,
docs/{hardware.md,status.md,booting-amigaos.md}. Full source content and notices
cached in work/derfsss-uboot-review-20261108; hashes in intake.json.
Discord identity remains unverified. This is U-Boot, not received Linux GPU patches.

## Concrete comparisons

1. video.c explicitly reports RX560/Vega64 testing on X5000, not A1222.
   status.md confirms A1222 AmigaOS boot and keyboard, but marks PCIe graphics
   console not independently verified. Do not relabel this as a proven A1222
   Linux/Polaris fix.
2. Firmware POST executes the card's x86 VBIOS, chooses a linear VBE mode and
   translates its PCI bus framebuffer address with pci_bus_to_virt. Geometry,
   pixel format and scanline pitch are validated. A useful basis for a separate
   firmware-framebuffer handoff investigation; no Linux simple-framebuffer node
   or physical Linux fbcon acceptance was established by this review.
3. VGA bridge forwarding explicitly opens legacy VGA/I/O decode during POST
   and restores it afterward. Comments describe X5000 Vega bridge machine checks.
   This solves a firmware POST routing problem; our existing stock firmware
   displays and Linux ring tests pass before DPM_Enable. It is not evidence that
   copying this temporary bridge workaround repairs our later DPM transition.
4. PCIE1 memory bus0xe0000000 maps to CPU physical0xc40000000, size512MiB;
   I/O physical0xfffc20000 maps to bus0. Our off-board boot capture already
   reports exactly these memory and I/O ranges. Historical tabor3.dts agrees.
   The gross outbound-map mismatch hypothesis is weakened; inbound DMA windows,
   coherency and GPU DPM table addresses remain distinct and unverified here.
5. The source describes fixed board clocks, PCIe1-only slot use, and reference
   board differences (no PIXIS/ICS307). Documentation leaves PCIe clock-chip
   contents and several straps unverified. These are comparison inputs, not
   measured corrections to our hardware.

## Next bounded action

Audit the DPM table's actual serialized addresses/values against the owning
SMU7 SRAM/firmware contract and inspect the transition path for platform PCIe
power/link assumptions. Ask contributor for exact Linux patches separately.
Firmware-framebuffer handoff can be pursued for a console independently of
accelerated AMDGPU. Do not flash this firmware or issue another GPU bind merely
because source is available. No hardware mutations performed in this review.

## Broader repository survey

GitHub connector repository search returned33 public repositories. Six READMEs
were reviewed; branch heads are recorded in repository-overview.json. This is
README-level qualification, not an implementation or licensing audit:

- MCP-AmigaOS4: native MCPd daemon plus host MCP server, file/command/task/screen
  and hardware inspection. README reports QEMU Pegasos2 and real X5000 validation;
  A1222 feature parity not independently established. Strong candidate for the
  earlier native OS4 remote-access requirement. SECURITY.md explicitly says the
  TCP daemon lacks authentication/encryption: retain isolated lab access. No
  install, agent registration, daemon launch or remote write performed.
- qemu-runner: compile/upload/run/capture cycle and native SerialShell; also
  supports real networked hardware. Documents os4-gcc6 fallback for misbehaving
  P1022 binaries. Relevant ABI comparison, not proof our GCC or Linux GPU defect.
- VirtIOGPU (archived): Picasso96/Workbench and Virgl paths for emulated GPU;
  not a physical Radeon driver. Status claims require reproduction.
- minQEMU: X5000/Sam460 AmigaOS-focused emulator; explicitly no Radeon/3D in
  this project's current scope. Cannot validate A1222 Polaris/PCIe/SPE behavior.
- VulkanOS4: software ICD and GPU ICD via existing ogles2/Warp3D Nova stack.
  Could provide useful OS4 rendering comparisons, but depends on the working
  OS4 GPU driver rather than supplying a Linux Polaris implementation.
- SandboxVM: driver/program iteration harness, explicitly no MMU isolation;
  not protection against physical PCIe bus lockups.

Other surfaced repositories include qemu, bboot, adtools, clib4, AmigaNVMeDevice,
usb3-amigaos4, rust-amigaos4-crate and RustSocket. They remain unreviewed here.
No dedicated Linux AMDGPU patch repository identified by this name/README
survey; code inside unreviewed repositories/branches remains an open question.
