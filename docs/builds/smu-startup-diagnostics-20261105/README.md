# Polaris SMU startup diagnostic candidate

Baseline: accepted physical6.12.113-tabor-modular, original firmware-upload
semantics, both Tabor board patches. The unproven LE-upload experiment is not
included. Complete firmware and13 module dependencies have already been
verified on hardware; no missing Polaris file found.

Source review found that smu7_upload_smu_firmware_image ignores return values
from cgs_get_firmware_info, and a related SMU7 message helper can report success
after missing replies. These are diagnostic/error-propagation weaknesses, not
proof of the current cause. Protection-mode startup also ignores some polling
and test-message results, leaving the final SMU_PASS check as its visible
failure. Do not change timeouts or bypass authentication based on that alone.

Isolated diagnostic patch logs selected firmware/name/version/size/offset,
protected/security mode, native versus LE interpretation of first word, and
existing PC/status/events/flags/response registers around controller startup.
Failed firmware lookup is propagated rather than uploading empty info. No
new reset/clock sequence, firmware modification or forced PCI writes.

Fresh source extraction and ordered board+diagnostic patches, exact retained
.config; disposable copy of accepted build outputs supplies generated kernel
headers and symbol metadata for a targeted AMDGPU module build. The reference
output/source is preserved. R730 container tabor-smu-diagnostics-build-003,
work/tabor-smu-diagnostics-20261105-003,4CPU/6GiB/network disabled, pinned
sha256:2781e11839beffa351f8c411d71b7e2bd1ae0336d24c60b407778c3350dd9da0.
Compilation and physical diagnostic results pending. Installed USB unchanged.

Attempt001 configured successfully but output-copy staging failed on an existing Kbuild source symlink, before compilation. Attempt002 preserves the freshly configured source link and copies the remaining reference outputs into its separate tree. No reference or installed USB files changed.

Attempt002 then failed before source compilation because relative M= selected an external-module layout without its Makefile in the output tree. Attempt003 uses the normal in-tree amdgpu.ko target and is compiling driver sources. Hardware selection review:1002:67ff/revisionff matches ASICID_IS_P21, so the hard-key SMU branch should select polaris11_k_smc.bin; the soft-key branch selects polaris11_smc_sk.bin. Runtime logs must confirm the branch. Both files are already verified in the complete package audit.
