# Clean frozen cross-build qualification

The previous native dependency superset contained1,279 installed packages.
It conflicted with util-linux's Build-Conflicts:libedit-dev before compilation.
The new root starts from the existing frozen buildd002 tar and adds native
apt-utils through normal apt. It has125 installed packages, clean dpkg audit
and apt check, preserved native foundation versions, and the expected native
apt solver. Broad native tools and1,155 cached archives remain on the server.

`extend-native-build-root.py` now accepts an explicit hash-pinned parent and
same-baseline metadata receipt. It reuses retained apt indexes and binds a
persistent package cache; apt update and signature validation remain enabled.
The initial root001 attempt was stopped during Snapshot metadata timeouts;
its logs remain. Root002 reused cached indexes and installed apt-utils without
fetching its cached archive. See root-receipt.json for tar/recipe/parent hashes.

The submitter accepts a reviewed --plan path. qualify-clean-root.json limits
the qualification to util-linux/PAM and their supported bootstrap requests,
using the same pipeline and standard builders as the workstation batch.
`port-qualification-20261104-001` is the first run with this root. Root creation
alone is not cross-build acceptance: real cache mounting, resolver selection,
dependency installation, SDK compilation and .deb inspection still need results.
No source/ABI/package-state override or target execution is introduced.

Qualification001 passed cache access and the old native libedit-dev conflict;
PAM installed genuine build dependencies and apt executed its external solver.
Both sources then failed acquisition, before compilation: Snapshot503/504 on
fakeroot and several native packaging helpers. See qualification-001-fallout.json.

A bounded same-origin transport probe used Debian apt-helper to fetch the exact
frozen fakeroot URI with `?download=1`, verified by the authenticated native
index SHA256. The reusable cache-frozen-native-archives.py accepts only explicit
package=version requests present in that hash-pinned index, invokes apt-helper
with the expected SHA256, and retains failures while caching successful files.
No live mirror or newer metadata is selected; apt still owns installation.
Native-cache-fill001 verified and cached fakeroot, python3-ruyaml and
strip-nondeterminism; dose-distcheck was already cached. Five requests still
failed Snapshot503/504. This route is a partial recovery, not a reliable mirror
fallback. Source intake for libevent/libtextwrap also stopped on Snapshot .dsc
acquisition; no unverified source lock or source build was registered.
Qualification002 retries the same clean-root plan with these newly cached inputs.
