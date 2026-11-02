# GCC runtime packaging and host SDK cleanup

The 73-source group remains the first graphical candidate's working scope.
Package count is not an installation or boot acceptance gate. The current
blocker includes missing installed target development dependencies, not just
missing compilations.

GMP203 compiled its C/C++ libraries, then Debian dependency generation could
not identify the owner of libstdc++. Its RUNPATH also contained `/tools`: the
bootstrap compiler's libtool archives retained the old SDK library path.

Changes in this round:

- Assemble real `libgcc-s1` and `libstdc++6` powerpcspe packages through debhelper
  from the recorded, patched GCC8.5 compilation. Validate source SHA512, patch
  hashes, complete original compiler tree identity, library ELF headers and
  absence of runtime search paths. Preserve upstream licensing and provenance.
  This is bootstrap packaging of existing compiled output, not a fresh Debian
  GCC source-package compilation. The original tools tree remains unchanged.
- Generate normal shlibs and binary dependencies. The C++ runtime depends on
  libc6 >=2.41 and the real libgcc-s1 package. No fake installed package records
  or hand-written replacement shlibs entries are introduced.
- Remove four libtool `.la` files only from the relocated native SDK package
  (8.5.0+tabor3); preserve compiler binaries and shared/static target libraries.
- Convert the actual target runtime packages through Debian dpkg-cross for the
  host build environment only. Keep those converted packages and the native SDK
  out of the target archive.
- Install those packages normally in a hash-checked offline build container.
  Use its installed `/usr/lib/tabor-spe-toolchain` compiler for fresh GMP301.

Recorded evidence:

- `target-runtime-receipt.json`: runtime003 completed; no target execution.
- `host-sdk-receipt.json`: cleaned compiler package and four removed archives.
- `cross-runtime-receipt.json`: real input/output hashes and dependencies.
- `environment-build.log`: all three package hashes verified; normal dpkg
  installation/configuration and audit succeeded.
- `context-provenance.json`, `context-SHA256SUMS`: reusable context recipe
  regenerated the same package inputs after the initial environment build.

Build environment:
`sha256:34575c073e8a81afdda9bd1bef50e49eab77e0c87972081b3c3b0b522825fade`.
The parent image is recorded in the runtime/cross receipts. Preparation:

```
python3 scripts/prepare-cross-development-context.py \
  --receipt WORK/runtime-cross-001/receipt.json \
  --host-toolchain-receipt WORK/host-sdk-clean-001/receipt.json \
  --dockerfile docker/Dockerfile.sdk-runtime-build-env \
  --output WORK/sdk-runtime-env-recipe-001 \
  libgcc-s1-powerpcspe-cross libstdc++6-powerpcspe-cross
```

All substantial work ran on R730. GMP301 is constrained to4 CPUs/6GiB; package
assembly/conversion used smaller isolated jobs. No QEMU PPC binfmt handler was
registered on the build host during inspection. Native generators and packaging
programs may run; target tests remain a separate QEMU/hardware gate. Initial
runtime001 used the wrong cache mount; runtime002 succeeded but lacked the
sysroot for a buildinfo compiler/header query. Runtime003 corrects both and is
the only preferred input. Neither incident demonstrated a target code failure.

GMP301 completed successfully: five packages (four powerpcspe binaries plus
one architecture-independent documentation package). Native readelf checks on
the fresh runtime libraries find no /tools, /work or compiler-prefix search
paths. Exact dynamic sections, generated dependencies and hashes are retained
in gmp301-validation.json; the build receipt is gmp301-receipt.json. Target
runtime tests did not run.

Signed archive010 now includes these real GCC runtime and GMP artifacts:64
artifacts total, up from57. apt update/signature and the selected library
installation simulation pass. Full Essential and desktop dependency closure
remain blocked (apt-check012.json); no configured root is claimed. An initial
apt-check010 used a planning profile lacking package_seeds and exited before
verification;011 omitted the archive mount at its declared /repo location.
Check012 corrects both orchestration inputs and uses the real VM132 session
seed profile. These were verification setup failures, not package failures.

Pending: remaining dependency closure, normally configured target root,
E rendering and physical A1222 boot.
No new graphical boot or USB write is claimed by these packaging results.
