# AMDGPU upstream source intake — 2026-11-07

Fetched sparse source checkouts on R730; no laptop compilation/extraction.
Mainline Linux pinned at d48723711bae9b8cdc56719c448ba42fef28cbee.
AMD maintainer drm-next pinned at5349075eac146ae0511d8929fc24451e4d9a4b7e.
The current mainline MAINTAINERS entry points to
https://gitlab.freedesktop.org/drm/amdgpu/kernel.git; ls-remote independently
verified its drm-amdgpu-next points to that same fetched AMD commit. The
maintainer transport was https://gitlab.freedesktop.org/agd5f/linux.git.

The sparse checkouts retain the AMD driver subtree, TTM, DRM/Linux headers,
GPU documentation and license files. AMD development also retains DRM UAPI,
PPC architecture headers, PCI controllers and license/process documentation.
The AMD subtree contains3096 tracked files. The rest of each Linux tree remains
available through the cached Git objects / partial-clone remote. This is the
in-kernel driver source, not a standalone driver package or userspace Mesa.

Receipts record commits and selected per-file SHA256. Reuse pinned checkouts;
do not refetch moving branches for each investigation. No target baseline,
module, firmware, boot media or saved U-Boot setting changed. Mainline and
AMD development are comparison references, not an authorized baseline refresh.

COPYING and LICENSES are preserved. Linux has GPL2 terms and per-file exceptions;
the inspected gfx_v8_0.c carries AMD's MIT-style permission/copyright notice.
Preserve file-specific notices with any reused code. No proprietary SDK or
firmware image was imported.

## First comparison

Retained exact relevant function bodies and selected file hashes for patched
6.12.113, mainline and AMD development in source-comparison.json.

- The same CP resume ordering remains: KIQ resume, GFX resume, KCQ resume,
  ring tests, then GUI-idle interrupt enable.
- Newer code accumulates and returns compute-ring test errors; old code ignores
  those return values. That is relevant error propagation, not proof that it
  prevents our bus hang.
- Newer GFX8 code retains the BE hardware BUF_SWAP path and native write-pointer
  shadows. Finding newer source therefore does not by itself establish a fix
  for the measured Polaris BE publication issues.
- The GFX IB self-test directly populates ib->ptr with native words, while ring
  submission uses a different writer. Follow all IB producers and publication
  before deciding where serialization belongs. Scratch-ring success alone does
  not validate this later path. No IB defect is established as the current
  hang: post-resource ring tests are still not individually bracketed.

Next bounded action: use these complete source contexts to trace the first
unobserved post-resource operation and compare ring versus IB/SDMA/fence
publication. Derfs' reportedly working patches remain to receive and compare.
No physical test or GPU fix was claimed during intake.
