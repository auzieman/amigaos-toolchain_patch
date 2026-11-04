# AppArmor library bootstrap

Frozen source: Debian apparmor4.1.0-1, retained source cache and checksum lock
profiles/port-dependency-sources.lock.json. The local patch changes Debian
packaging only; upstream library code and license notices remain untouched.

Its C library is needed by D-Bus/systemd, but the original source build also
requires target Apache and Python development packages for optional outputs.
The explicit stage1 profile builds only libapparmor1/libapparmor-dev through
normal debhelper and upstream library makefiles, without language bindings.
Other binary stanzas are excluded in stage1. The normal profile retains all11
original binary package stanzas and existing recipes. This does not establish
full AppArmor parser, Python, PAM or Apache-module support; the registry keeps
full rebuild required, and stage1 output must not satisfy that acceptance gate.

Validation: initial draft failed git apply source preparation due to a malformed
EOF diff boundary; no compilation used that draft. The corrected patch passes
`git apply --check` against the exact cached extraction. Native Debian
`dh_listpackages` returns2 library packages in stage1 and all11 without stage1.
Native make --dry-run shows only library build/install and normal dh_install
for stage1. Actual source packaging, dose installability, cross compilation,
coinstallation and target execution remain separately required gates.
