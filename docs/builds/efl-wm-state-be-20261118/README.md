# EFL on big-endian: windows read as withdrawn, so Elementary never renders them (#8) - 2026-11-18

## Problem

Under Enlightenment, every Elementary window had its frame and title drawn by E, but its interior
showed nothing. This affected Terminology, `elementary_test`, and E's own dialogs. Where nothing lay
behind a window the interior looked black, which is the #8 symptom. It was seen in the SPE QEMU guest
and, per the forge checkpoint of 2026-11-16, on the A1222.

## Cause

`ecore_x_icccm_state_get` (EFL 1.28.1, `src/lib/ecore_x/ecore_x_icccm.c:63-71`) reads the ICCCM
`WM_STATE` property and compares its first *byte*, `prop_ret[0]`, against `WithdrawnState` (0),
`NormalState` (1) and `IconicState` (3). `WM_STATE` has format 32, and Xlib returns format-32
data as an array of `long`.

On a big-endian host, `NormalState` is stored as the bytes `00 00 00 01`, so the first byte is 0
and every window that the window manager marks Normal reads back as Withdrawn. `ecore_evas_x` then
keeps `prop.withdrawn` set (`ecore_evas_x.c:975-1000`), and Elementary's `auto_norender_withdrawn`
puts the window into manual render. The window never renders its first frame. Its client-side
frame, the parent of all content, therefore stays hidden at 0x0, and nothing is drawn. On
little-endian the first byte is the low byte, so the code works there.

The fault depends on byte order, not on SPE. That is why QEMU, with IEEE softfloat, and the A1222
both show it.

## Patch

`patches/efl/0001-ecore-x-icccm-wm-state-format32.patch` against Debian efl 1.28.1-1 (with
`patches/efl/series.json`; patch 0002 is the second instance, see the sweep below) reads the element: `long state = ((long *)prop_ret)[0];`, and also
requires `format_ret == 32`. `scripts/build-efl-session.py` now applies `patches/<name>/series.json`
for `efl` as it already did for `e17`. The seven `profiles/sbuild` batch plans that build `efl`
now name the series under `patch_series`, which is how `run-ready-sbuild-batch.py` hands a reviewed
quilt series to `run-sbuild-package.py`; on a fresh `efl_1.28.1-1` source the patch applies with
`quilt push` at `--fuzz=0` after Debian's own patches. Nothing changes on little-endian.

## How it was found (A1222, kernel 020)

auzieman's session chain was built unmodified on the build-server replica with the GCC14 SPE SDK:
`build-desktop-base.py`, then `build-x11-clients.py`, `build-session-deps.py` and
`build-efl-session.py` (`scripts/e8-build.sh`). The SDK needed two adjustments, and neither touches
the recipes:

- it has no built-in sysroot, so `/spetools` holds gcc/g++/cpp wrappers that add `--sysroot`
  (libtool's shared links drop the `--sysroot` in CFLAGS);
- its `libatomic` goes in through `--extra-stage`, as auzieman's libatomic001 did for GCC8.

The stage runs on the A1222 as a chroot in its own tmpfs (`scripts/e8-chroot.sh`,
`scripts/e8-board-setup.sh`; tarball `21f416fd...`). Its glibc is the SDK sysroot's, the same one
it was linked against. Xvfb runs at 1280x720x24, with MIT-SHM working because the 020 kernel has
SysV IPC.

1. **X server readback** (`probes/x8-redirect.c`, `hw/testa-020.txt`). A Composite-redirected
   window was filled with four colours and read back three ways, at depth 24 and 32: XGetImage of
   the window, XGetImage of the pixmap, and XShmGetImage of the pixmap. All 24 pixel checks pass.
   The server's big-endian Composite/GetImage path is correct.
2. **E session** (`scripts/e8-testb.sh`, `probes/x8-shot.c`, `hw/testb-before-020.txt`,
   `hw/e-clients-before.png`). Under E, the Terminology, `elementary_test` and E dialog interiors
   show the wallpaper (nothing drawn), with frames correct.
3. **Plain Evas** (`probes/x8-ee.c`). An `ecore_evas` software_x11 window with rectangles reads back
   correctly from the server. Evas and its X11 output are fine.
4. **Theme numbers** (`probes/x8-convert.c`, `hw/convert-020.txt`). Doubles round-trip exactly
   through `eina_convert_dtoa`/`atod` and Eet. The only refusals are -0 and Inf, which are
   format-inherent, so theme data decodes correctly.
5. **Elementary scene** (`probes/x8-elm.c`, `hw/elm-scene-before-020.txt`). `elm_win` is 300x200 and
   visible, but its frame Edje object is 0x0 and hidden, and all content sits under it.
6. **Render state** (`hw/elm-scene-render-020.txt`). After 2 s: 0 renders, `manual_render 1`,
   `withdrawn 1`, window 100% black. One forced `ecore_evas_manual_render` gives a 300x200 frame,
   0% black and the theme grey `606060`.

## Result with the patch

| | before | `libecore_x` patched in place (`e3017062...`) | EFL rebuilt through `build-efl-session.py` with the series (`921b6ffd...`) |
|---|---|---|---|
| E's dialogs (10, depth 32), share of black pixels | 30-35%, interiors empty | 0%, text, icon and buttons drawn | same |
| `elementary_test` under E | interior empty | complete UI (`hw/e-clients-after.png`) | same |
| Terminology under E | interior empty | prompt and cursor (`hw/terminology-after.png`) | same |

The before/after logs are `hw/testb-before-020.txt`, `hw/testb-ecorex-fix-020.txt` and
`hw/testb-efl002-020.txt`. Kernel taint stayed 0 throughout. The unpatched library is `935d0824...`.

## Sweep for the same defect (format-32 X properties read by byte)

Only `ecore_x` calls Xlib's property functions directly in EFL 1.28.1 and E 0.27.1, so the audit
covered two groups.

The first group is the 26 raw `XGetWindowProperty`/`XChangeProperty` sites in five files:
`ecore_x_window_prop.c`, `ecore_x_keygrab.c`, `ecore_x_window.c`, `ecore_x_netwm.c` and
`ecore_x_icccm.c`. Apart from `WM_STATE`, they read through `unsigned long *`, or write `long`,
`int` or `CARD32` buffers, which are all 4 bytes on PPC32, or real format-8 strings.

The second group is the callers of `ecore_x_window_prop_property_get`/`_set`. The helper converts
format-32 data to and from `unsigned int` arrays in host order.

| caller | reads/writes format-32 data as | verdict |
|---|---|---|
| `ecore_x_icccm.c:65` `ecore_x_icccm_state_get` (`WM_STATE`, raw) | first byte | **defect, patch 0001** |
| `ecore_x_dnd.c:185` `ecore_x_dnd_version_get` (`XdndAware`) | `(int)*prop_data`, first byte | **defect, patch 0002** |
| `ecore_x_dnd.c` type/action lists, `ecore_x_events.c` XDND types, E `xwayland/dnd.c` | `Ecore_X_Atom *` | correct |
| `ecore_x_mwm.c` Motif hints | `MWMHints` of `CARD32` | correct |
| `ecore_x_icccm.c` `WM_COLORMAP_WINDOWS` | `Window *` (4 bytes on PPC32) | correct here |
| `ecore_x_e.c` profiles and rotation lists | `Ecore_X_Atom *`, `int *` | correct |
| `ecore_x_events.c` selection targets, `_ecore_x_selection_parser_targets` | `int *` | correct |
| E `e_comp_x.c` `_GTK_FRAME_EXTENTS`, `e_backlight.c` `XFree86_has_VT` | `int *` | correct |
| setters: `ecore_x_dnd.c`, `ecore_x_mwm.c`, `ecore_x_icccm.c`, `ecore_x_e.c`, `ecore_evas_x.c` | `int`, `unsigned int` or `Ecore_X_Atom` arrays | correct |

No ClientMessage handler reads 32-bit data through `data.b[]`. E's XSETTINGS blob is format 8 and
writes its byte-order marker from `__BYTE_ORDER` (`e_xsettings.c:350`).

**Effect of 0002.** On big-endian, `ecore_x_dnd_version_get` returned 0 for every XDND-aware window.
Its two callers treat 0 as "not aware":
- the drag source walks past every drop target (`ecore_x_dnd.c:674`);
- an incoming drag's source is rejected (`ecore_x_dnd.c:435`).

So drag and drop between X windows could not work. `probes/x8-dnd.c` marks a window XDND-aware and
reads the version back; `hw/xdnd-version-020.txt` and `hw/xdnd-version-efl003-020.txt` hold the
results:

| `libecore_x` | raw `XdndAware` | `ecore_x_dnd_version_get` |
|---|---|---|
| unpatched (`935d0824`) | 5 | 0 |
| 0001 (`921b6ffd`) | 5 | 0 |
| 0001 + 0002, rebuilt through `build-efl-session.py` (`1fd8e3fa`) | 5 | 5 |

With 0001 + 0002 the E session is unchanged from 0001 alone: every client and dialog is 0% black
(`hw/testb-efl003-020.txt`). Both patches pass `git apply --check` and `quilt push --fuzz=0` on a
fresh `efl_1.28.1-1` source. An actual drag between two windows was not performed.

Outside this class: `ecore_x_image_is_argb32_get` (`ecore_x_image.c:461`) checks `BitmapBitOrder`
where the pixel layout follows `ImageByteOrder`. The two agree when client and server have the
same byte order, so it can only matter across endianness (for example a big-endian client on a
little-endian X server over the network). It was not changed.

## Ruled out along the way

- **SPE arithmetic.** The symptom also appears under QEMU's IEEE softfloat, and it now has a
  byte-order cause.
- **E's compositor readback.** `ecore_x_image_is_argb32_get` checks `BitmapBitOrder` where it
  should check `ImageByteOrder`, but the two agree on an all-big-endian setup. Test 1 shows the
  server side is correct.
- **The missing `e_comp.cfg`.** E 0.27.1's standard profile does not ship one.
- **`eina_convert_dtoa` "non-finite" log line.** Eet refuses to encode Inf by design (see test 4).
- **`evas_render_rendering_wait` timeout.** It did not occur on the A1222.

## Not covered

- **Without a window manager**, an Elementary window stays withdrawn and undrawn even with the
  patch, because nobody sets `WM_STATE`. `ELM_AUTO_NORENDER_WITHDRAWN=0` did not change that. It is
  not #8's case, and whether little-endian behaves the same was not checked.
- **E's remaining dialogs** come from this test chroot, not from EFL: "cannot change working
  directory to root's home" (no `/root`) and module-load errors for modules this build disables.
- **No Debian package build of EFL with the patch.** Neither the physical A1222 Xorg session from
  the forge checkpoint nor the QEMU guest was re-run.
