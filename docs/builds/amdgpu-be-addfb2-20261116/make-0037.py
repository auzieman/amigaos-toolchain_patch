#!/usr/bin/env python3
"""Edit dce_v11_0.c for #35: host-byte-order framebuffers on big-endian.

Usage: make-0037.py <path to dce_v11_0.c>   (edits in place; fails if any anchor is missing)
"""
import sys

path = sys.argv[1]
src = open(path).read()


def sub(old, new):
    global src
    if src.count(old) != 1:
        sys.exit(f"anchor not found exactly once: {old[:60]!r}")
    src = src.replace(old, new)


# 1. XRGB8888/ARGB8888 are little-endian by definition: no swap once the quirk is set.
#    BGRX8888/BGRA8888 (= host-order XRGB/ARGB on BE) scan out as ARGB8888 with ENDIAN_8IN32.
sub("""	case DRM_FORMAT_XRGB8888:
	case DRM_FORMAT_ARGB8888:
		fb_format = REG_SET_FIELD(0, GRPH_CONTROL, GRPH_DEPTH, 2);
		fb_format = REG_SET_FIELD(fb_format, GRPH_CONTROL, GRPH_FORMAT, 0);
#ifdef __BIG_ENDIAN
		fb_swap = REG_SET_FIELD(fb_swap, GRPH_SWAP_CNTL, GRPH_ENDIAN_SWAP,
					ENDIAN_8IN32);
#endif
		break;
""", """	case DRM_FORMAT_XRGB8888:
	case DRM_FORMAT_ARGB8888:
		fb_format = REG_SET_FIELD(0, GRPH_CONTROL, GRPH_DEPTH, 2);
		fb_format = REG_SET_FIELD(fb_format, GRPH_CONTROL, GRPH_FORMAT, 0);
		/*
		 * Little-endian in memory by definition. On big-endian hosts
		 * quirk_addfb_prefer_host_byte_order is set, so host-order
		 * framebuffers arrive as BGRX8888/BGRA8888 below.
		 */
		break;
#ifdef __BIG_ENDIAN
	case DRM_FORMAT_BGRX8888:
	case DRM_FORMAT_BGRA8888:
		/* Host-order XRGB8888/ARGB8888: swap each 32-bit word. */
		fb_format = REG_SET_FIELD(0, GRPH_CONTROL, GRPH_DEPTH, 2);
		fb_format = REG_SET_FIELD(fb_format, GRPH_CONTROL, GRPH_FORMAT, 0);
		fb_swap = REG_SET_FIELD(fb_swap, GRPH_SWAP_CNTL, GRPH_ENDIAN_SWAP,
					ENDIAN_8IN32);
		break;
#endif
""")

# 2. Primary plane with the host-order formats on big-endian.
sub("""static int dce_v11_0_crtc_init(struct amdgpu_device *adev, int index)
{
	struct amdgpu_crtc *amdgpu_crtc;
""", """#ifdef __BIG_ENDIAN
static const uint32_t dce_v11_0_primary_formats_be[] = {
	DRM_FORMAT_BGRX8888,	/* host-order XRGB8888: legacy ADDFB 32/24, fbdev */
	DRM_FORMAT_BGRA8888,	/* host-order ARGB8888: legacy ADDFB 32/32 */
	DRM_FORMAT_XRGB8888,
	DRM_FORMAT_ARGB8888,
};

static const struct drm_plane_funcs dce_v11_0_primary_plane_funcs = {
	DRM_PLANE_NON_ATOMIC_FUNCS,
};

static int dce_v11_0_crtc_init_be(struct drm_device *dev, struct drm_crtc *crtc)
{
	struct drm_plane *primary;
	int ret;

	primary = kzalloc(sizeof(*primary), GFP_KERNEL);
	if (!primary)
		return -ENOMEM;
	ret = drm_universal_plane_init(dev, primary, 0,
				       &dce_v11_0_primary_plane_funcs,
				       dce_v11_0_primary_formats_be,
				       ARRAY_SIZE(dce_v11_0_primary_formats_be),
				       NULL, DRM_PLANE_TYPE_PRIMARY, NULL);
	if (ret) {
		kfree(primary);
		return ret;
	}
	/* Same as drm_crtc_init(): legacy SETCRTC skips the format check. */
	primary->format_default = true;
	ret = drm_crtc_init_with_planes(dev, crtc, primary, NULL,
					&dce_v11_0_crtc_funcs, NULL);
	if (ret) {
		drm_plane_cleanup(primary);
		kfree(primary);
	}
	return ret;
}
#endif

static int dce_v11_0_crtc_init(struct amdgpu_device *adev, int index)
{
	struct amdgpu_crtc *amdgpu_crtc;
""")

sub("""	drm_crtc_init(adev_to_drm(adev), &amdgpu_crtc->base, &dce_v11_0_crtc_funcs);
""", """#ifdef __BIG_ENDIAN
	if (dce_v11_0_crtc_init_be(adev_to_drm(adev), &amdgpu_crtc->base)) {
		kfree(amdgpu_crtc);
		return -ENOMEM;
	}
#else
	drm_crtc_init(adev_to_drm(adev), &amdgpu_crtc->base, &dce_v11_0_crtc_funcs);
#endif
""")

# 3. Tell the DRM core that legacy formats are host order, which also unblocks ADDFB2.
sub("""	adev_to_drm(adev)->mode_config.fb_modifiers_not_supported = true;
""", """	adev_to_drm(adev)->mode_config.fb_modifiers_not_supported = true;
#ifdef __BIG_ENDIAN
	adev_to_drm(adev)->mode_config.quirk_addfb_prefer_host_byte_order = true;
#endif
""")

if "#include <drm/drm_plane_helper.h>" not in src:
    sub("#include <drm/drm_modeset_helper_vtables.h>\n",
        "#include <drm/drm_modeset_helper_vtables.h>\n#include <drm/drm_plane_helper.h>\n")

open(path, "w").write(src)
print("edited", path)
