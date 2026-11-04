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
