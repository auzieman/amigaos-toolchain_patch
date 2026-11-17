# Boolean custom glGet values on big-endian hosts

`0001-get-boolean-custom-values-via-value-bool.patch`, against Debian mesa 25.0.7
with `debian/patches/series` applied. Apply with `patch -p1` from the source root.
Mesa MIT licence; this does not relicense anything.

## The bug

In `src/mesa/main/get.c`, `find_custom_value` fills four `LOC_CUSTOM, TYPE_BOOLEAN`
entries through `v->value_int`:

- `GL_TRANSFORM_FEEDBACK_ACTIVE`
- `GL_TRANSFORM_FEEDBACK_PAUSED`
- `GL_DEBUG_OUTPUT`
- `GL_DEBUG_OUTPUT_SYNCHRONOUS`

The readers take the union's first byte as a `GLboolean`. On a big-endian host
that is the high byte of the `GLint`, so all four always read `GL_FALSE`. The
patch stores them in `v->value_bool`.

I checked every `LOC_CUSTOM, TYPE_BOOLEAN` entry in 25.0.7's
`get_hash_params.py`: these four are the only ones filled through `value_int`.
The same code is in Mesa 26.2.3.

## Evidence

**25.0.7, compile only.** The patch applies to the replica's 25.0.7 tree and
builds incrementally with the GCC14 SPE SDK (tabor2) with no warnings, and
`libgallium-25.0.7.so` changes. It was not run on hardware with 25.0.7.

**Same change on a Mesa 26.2.3-based big-endian Linux tree, A1222.** Setup:
Polaris11 RX 550, kernel 019 (#49) with `polaris11_le_user_ib=1`, tabor3 SPE
userland. Results:
- The 8 dEQP GLES3 `state_query.boolean.transform_feedback_*` fails pass.
- Every `state_query` case passes.
- Full GLES3 mustpass, without `builtin_functions.precision`: 43312 Pass, 21 Fail,
  none of them state queries.
