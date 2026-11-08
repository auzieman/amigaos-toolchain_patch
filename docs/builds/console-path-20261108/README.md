# Historical neighboring DCE10 console test

**Correction:** RX560/Polaris11 selects dce_v11_2_ip_block with DCE11 callbacks,
not DCE10. This result remains a neighboring-generation comparison and is not
target display qualification. See ../console-selected-path-20261108/ for the
corrected source selection and tests.

# Verify the basic console path separately from ring tests

Candidate006is configured for legacy DCE10 display (CONFIG_DRM_AMD_DC is off),
AMDGPU/DRM modules, DRM fbdev emulation, built-in VT/fbcon and8x16fonts. The
actual probe invokes drm_fbdev_ttm_setup(...,32) after successful load and DRM
registration, only when mode configuration exists and connectors are present.
A power-state fault before completing registration can prevent reaching that
setup even when the display hardware IP's hw_init returned success.

## Actual-source pixel and surface test

`test_console.py` extracts the complete dce_v10_0_crtc_do_set_base function and
the generic drm_fbdev_ttm_damage_blit_real function. It uses the pinned DCE10
register definitions/enums and DRM fourcc constants, with mocked BO/register/
iosys endpoints.64successful scenarios per architecture cover16formats,
atomic/non-atomic modes and twoCRTCregister offsets. Checks include native
pixel bytes through damage rectangles with sentinel padding, surface address
high/low words, pixel pitch, viewport alignment and dimensions, reserve/pin
calls and format-specific swap settings.3,200modeled fetched pixel words match
between x86 and PPC32BE. Four failure/no-FB cases validate error/no-write paths.

This is two actual driver/core functions, not a handwritten replacement for
the surface programmer. Tiling metadata is fixed to linear. Pixel fetch is a
model of the programmed endian mode, not an observation of physical scanout;
channel crossbars, EDID, PLL/link training, fbcon glyph drawing and panel timing
are not hardware-validated by it. Initial compile errors were fixture header
selection issues: DCE10 owns its enum constants; mixing legacy SID macros with
those enums was removed. No production source change was made.

## Boot and console selection

`audit_boot.py` checks SanDisk serial03001919041721081205/PARTUUIDa1221105-02,
requires unmounted partitions, mounts rootro,noload and FATro, then unmounts
both in finally blocks. No files are changed or journal replay requested.

The active boot.scr selects e2e-003, not006. It has console=ttyS0,115200 followed
by console=tty0, and init=/init. The editable boot.cmd is stale and names the
old /boot/e2e path; boot.scr is the executed artifact. Its old console banner
also names001even though it loads003. These stale labels should be corrected
when preparing a separately reviewed installation, not mistaken for loaded
kernel identity. No boot script was regenerated here.

The root contains a native ELF /init, not Debian inittab/systemd/getty setup.
ItsSHAf4adcd1fee09de1ba8c96f5bc7dd75f6ee920dcc2455ac7d198826cafa10a761
matches the retained layered rescue root. Its strings includeSHELL_READY,
/dev/tty1,TERM=linuxand/etc/start-network. The retained init-shell.c selects
the last console token, maps tty0to tty1, acquires that tty and launches a root
bootstrap shell while starting networking independently. This test root should
show a shell, not a getty login prompt. No new account/service setup is needed
merely to reach that intended diagnostic prompt.

## Onboard fallback is not implemented

CONFIG_FB_FSL_DIU=yand the DTB contains an fsl,diu node, but the selected Tabor
board source explicitly has no DIU integration and supplies no set_pixel_clock
hook. The actual fsl-diu-fb init checks that hook and returns-ENODEV when absent.
Thus compiling the driver did not establish a usable onboard fallback or a
reason to move the monitor there. This review makes no DIU board-clock/pinmux
patch and no assumption that VESA/x86BIOS services exist on this board.

## Acceptance

Fourteen offline suites pass after adding this test; overall physical
acceptance remainsBLOCKED. The basic pixel-copy/surface-programming contracts
now have direct source tests, and console configuration/boot selection are
recorded. Actual Radeon framebuffer registration, connector/modeset success
and stable readable output must still be measured on hardware with candidate006.
USB remains003and unmodified; no GPU access or reboot occurred in this review.
