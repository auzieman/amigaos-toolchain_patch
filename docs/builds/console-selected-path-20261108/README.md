# Selected RX560 initialization and 2D display path

## Correction to the earlier console review

The physical e2e-003 log adds display block dce_v11_0. Pinned vi_set_ip_blocks
selects dce_v11_2_ip_block for CHIP_POLARIS11 with DC disabled; that descriptor
uses dce_v11_0_ip_funcs. DCE10 is a neighboring-generation path and the earlier
console-path-20261108 tests did not establish target display qualification.
Those historical results are retained with a correction. This increment tests
DCE11 and records the actual IP descriptor and callback selection in
selected-path.json and polaris-ip-selection.c.txt.

The exact nonvirtual/DC-disabled IP order is common, GMC8.1, Tonga IH, GFX8,
SDMA3.1, PowerPlay, DCE11.2, UVD6.3 and VCE3.4. Revision descriptors can reuse
shared implementation functions; file names alone are not selection evidence.

## Walk from initialization to console

1. Device IP initialization establishes memory, interrupts, engines, power and
   display blocks. DCE11 sw_init creates CRTCs and parses the BIOS object table
   into connectors. The physical003log already lists DisplayPort, HDMI and DVI
   connectors; this supports object discovery, not connected-sink/EDID success.
2. DCE11 hw_init initializes golden registers, VGA state, display power gating,
   digital encoders, DISPCLK/DPREFCLK, HPD and pageflip interrupts. These helpers
   submit ATOM commands; returning from hw_init is not physical PLL/link proof.
3. Device late_init runs selected late callbacks and power/clock gating.
   Corrected0024native clock decoding and0025/0026error propagation address
   the later PowerPlay transition source path seen around the003fault.
4. Device init queues delayed IB tests. These are asynchronous, and may overlap
   later console work. A briefly visible console would not qualify all IB or
   UVD payload contracts or establish stability through delayed tests.
5. After load/DRM registration, amdgpu_pci_probe selects32bpp TTM fbdev when mode
   configuration and connectors exist. Required KMS/TTM helpers are modules;
   I2C/I2C_ALGOBIT, VT/fbcon/fonts and fbdev emulation are enabled. The normal
   Kbuild/depmod bundle contains43modules;687imported AMDGPU CRCs are verified.
6. DRM's fbdev client probes cached/physical connector modes and selects a mode.
   DCE11 mode_fixup binds encoder/connector, applies scaling, prepares the PLL
   and rejects missing non-DP PLL selection. Mode_set programs clock/timing,
   surface, overscan/scaling/cursor and software hardware-mode state. Commit/
   encoder helpers enable the output. The generic TTM shadow-buffer damage
   helper copies fbcon pixel bytes to the mapped framebuffer.
7. Readable, stable output still requires real HPD/DDC/EDID, PLL/transmitter link,
   VRAM visibility, scanout and VT binding. Offline request equality cannot
   establish these electrical/firmware effects.

## Source tests and confirmed defect

The selected DCE11 complete surface function plus actual generic TTM damage
copy pass64success+4error/no-FB scenarios per architecture across16formats.
Tests cover32bpp console and smaller formats, addresses/pitch/viewport, BO
reserve/pin and3,200modeled fetched pixel words. Register and BO endpoints are
mocks; only linear tiling is modeled. Color crossbar output and timing are not
physical observations.

Actual atombios_crtc.c pixel-PLL, DCE clock and DTD timing functions plus their
PLL-source helper pass392scenarios/architecture and two invalid-header checks.
The tests exercise six pixel table revisions, four clocks, HDMI/DVI/DP,
color-depth settings, DCE clock requests and timing borders/sync flags. All
8,192emitted request bytes match x86/PPC. Current raw VBIOS revision has not
been captured, so revisions are test inputs, not claimed board observations.
The ATOM endpoint records requests/echoes a clock field; it does not program
hardware. Existing void PLL/timing APIs can discard interpreter errors; this
pass does not claim those APIs now propagate errors end-to-end.

The actual DCE11 mode_set caller ignored the error from its surface programmer,
then proceeded through remaining setup and updated hw_mode. Patch0027returns
that error immediately. The connected actual caller/surface regression uses
original code as a negative control across40scenarios/version/architecture,
160total, including failed reserve/pin/format and missing adjusted clock. Fixed
code preserves errors and skips false mode publication. Success behavior stays
unchanged. This repairs a verified error path, not the initiating003PCIe fault.

Sixteen aggregate offline suites pass after replacing the neighboring DCE10
suite with DCE11 and adding display ATOM/mode-set tests. The overall physical
acceptance gate remains BLOCKED with unresolved contracts recorded.

## Candidate and next hardware evidence

Isolated candidate007adds0027to006. It completes full kernel/modules/DTB/U-Boot
bundle qualification,43modules and687AMDGPU imported symbol CRCs. See
build-receipt.json for compiler, config, patch-chain, firmware and artifact
hashes. The SanDisk is unchanged and still selects003.

collect-console-state.sh is a prepared read-only/cached-state collector for
007. Run only over the existing SSH session after a fresh successful normal
bind returns, with off-board logging and rootRO established by the existing
physical harness. It refuses other kernel releases. It does not bind, force
connector detection, read registers, paint a framebuffer or retry after faults.
It records /proc/fb, framebuffer geometry, VT binding, cached connector modes
and device nodes. Kernel/sysfs locks can still block if the device is already
wedged; this is not recovery tooling. Visual confirmation remains separate and
is explicitly PENDING even when framebuffer registration succeeds.

The onboard DIU lacks the required board pixel-clock hook and is not a working
fallback. We are qualifying Radeon KMS on the actual A1222/card combination.
