# Read and execute the shared translation and console path

This review follows the selected candidate007 source through the BIOS
interpreter and actual Linux glyph renderer. It adds no kernel patch and does
not change the boot media. The earlier display buffer tests substituted the
ATOM execution endpoint; that gap is now exercised with the real engine.

## Concrete console execution chain

console-source-chain.json pins53reviewed function bodies, files and line
anchors, including direct and callback handoffs. It is a source walk, not a
record of hardware execution.

- amdgpu_pci_probe -> amdgpu_driver_load_kms -> amdgpu_device_init -> IP init /
  late_init. The selected Polaris display descriptor is DCE11.2 with shared
  DCE11callbacks. PowerPlay transitions and delayed IB work remain prerequisites
  for a stable initialized device, even though glyph rendering itself is CPU
  software.
- Successful load and DRM registration -> drm_fbdev_ttm_setup ->
  drm_client_register -> fbdev client's hotplug callback ->
  drm_fb_helper_initial_config. Client mode probing chooses connector/CRTC
  modes; no usable sizes returnsEAGAINand defers setup rather than producing a
  framebuffer.
- The fbdev probe allocates a client dumb framebuffer and system-memory shadow,
  fills fb_info, sets deferred IO and registers the framebuffer. The driver's
  dumb-create callback is amdgpu_mode_dumb_create in amdgpu_gem.c, not the
  similarly named display source file.
- Framebuffer registration triggers fbcon binding. fbcon_init / fb_set_par ->
  drm_fb_helper_set_par -> client legacy modeset commit ->
  drm_mode_set_config_internal -> amdgpu_display_crtc_set_config -> DRM CRTC
  helpers -> selected DCE11mode_fixup/prepare/mode_set/commit and encoder
  callbacks. Patch0027preserves surface-programming failures at this handoff.
- fbcon_putcs -> bit_putcs -> fb_imageblit deferred wrapper -> sys_imageblit
  expands font bits into native pixel words in the shadow buffer. Deferred
  damage -> TTM damage helper -> mapped framebuffer byte copy. DCE11surface
  programming supplies VRAM address, pitch, viewport, format and hardware
  pixel swap; the display engine fetches those pixels.

There is no requirement to emulate x86 instructions to render these console
pixels. The relevant contracts are software data formats and device accesses.

## Actual interpreter, not a replacement

The test compiles1,272lines of the actual atom.c execution engine, including
its source/destination decoders, opcode handlers, dispatch table and nested
execution. atom-bits.h retains its byte-based ROM readers. Linux allocation,
locks and time are shimmed; register endpoints use numeric memory models.

For valid streams the central contract is:

native caller values -> LE parameter bytes -> interpreter PS decoder -> native
workspace/arithmetic/register values -> register accessor; returned PS values
are serialized LE again. Native software workspace/scratch values must not be
blanket-swapped as though they were hardware wire buffers.

656cases per architecture cover1..32parameter words, nonpalindromic inputs,
PS->WS->register->PS round trips, every byte/word partial-write position and
nested table parameter offsets. All34,496emitted bytes match x86/PPC32BE.

The connected display test sends the actual display PLL/DCEclock/DTD request
buffers through that engine rather than returning a fabricated response.
392display scenarios per architecture retain8,192matching bytes. Two deliberate
negative controls remove either PS input decoding or PS output serialization.
Both still pass on x86 and fail on PPC, showing that the test detects the
missing conversion instead of accepting a mutually wrong host/device model.
The instruction streams transport the real caller buffers but are synthetic;
they are not the card's uncaptured VBIOS programs and do not program a PLL.

## Actual glyph-to-framebuffer path

The glyph test compiles sys_imageblit's actual monochrome paths, the actual
8x16kernel font, generic TTM damage copier and DCE11surface programmer.
All256glyphs at8/16/32bpp and two placements produce matching expected font
pixels through the complete tested byte path:1,536cases and196,608glyph pixels
per architecture. Padding and untouched pixels are checked. The pixel consumer
uses the programmed swap policy; its physical effect is not observed.

This qualifies the tested CPU-render/serialization path. It does not test VT
input, terminal escape parsing, scrolling, physical channel colors, EDID/DDC,
encoder links, firmware effects, VRAM coherency or scanout timing.

## Cumulative boundary reconciliation

The complete-word ATOM clock helper serializes once before the interpreter;
the interpreter decodes it once into a native value. The native V1PowerPlay
clock constructor correction0024is earlier in the flow: a bogus native clock
must not be hidden by globally changing the interpreter's correct LE access.
SMU table fields still use their documented BE conversion, separately from
ATOM's LE parameter space. Native fbcon pixels go through a byte-preserving
TTMcopy and format-specific DCE swap; they do not pass through the command-ring
serializer. These are different objects with explicit owning boundaries, not
one undifferentiated stream to swap globally.

An unrelated interpreter bounds concern surfaced during this walk: parameter
capacity is supplied as bytes while indexed PS accesses and ps_shift use
32-bit units. An upstream September2026discussion proposes guarding nested
underflow, but that proposal alone does not establish the unit contract or
our board's failure cause:
https://lists.openwall.net/linux-kernel/2026/09/23/2104
The current upstream engine also exposes the same interfaces:
https://github.com/torvalds/linux/blob/master/drivers/gpu/drm/amd/amdgpu/atom.c
No bounds patch was silently applied or treated as an endian fix. The valid
stream tests above do not qualify malformed bytecode handling.

## What is established and what remains

Nineteen aggregate suites pass. This pass executes previously mocked software
handoffs and preserves source anchors; it does not add a new kernel candidate.
007remains the compiled candidate, and003remains on the SanDisk.

The measured003fault follows a power-state command.0024corrects a demonstrated
native-clock defect feeding that path. The fixed-source prediction is removal
of the byte-reversed98530000clock and preservation of the original supported
clock table when selecting a listed clock. The exact selected raw state and
complete physical table were not captured, so a precise next mask or firmware
response is not invented from the x86maskfftrace.

A stable console requires that initialized device to reach successful DRM /
fbdev registration and physical mode/link/scanout. Those remaining observations
are specific hardware gates, not uncertainty about how the tested glyph and
parameter bytes are built. The synthetic interpreter programs cannot replace
an actual board VBIOS/firmware execution trace.
