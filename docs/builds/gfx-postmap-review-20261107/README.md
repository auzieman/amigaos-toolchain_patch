# 6.12 AMDGPU source review and errand breakpoint

Live A1222 stays on6.12.113-tabor-modular, original installed AMDGPU unbound.
This review performs no device load/reset, reboot, USB changes or kernel install.
The main project remains Trixie userspace on the working6.12 board kernel;
AMD7.3 is only a source comparison here.

## Findings

The last successful measured operation in gfx-map-stage hardware-offboard-001
was a KIQ scratch test after the eighth MAP_QUEUES. That verifies control-ring
progress, not actual compute-ring execution. The22 GPU MQD readbacks establish
sampled GPU-visible bytes, not all descriptor semantics or all later activity.
Roughly53ms after the final submission marker the log reports PCIe errors.
There is no successful post-mapping GFX/compute/SDMA marker in that capture.

Source order after mapping is GFX scratch test, KIQ scratch test, eight compute
scratch tests, GUI-idle interrupt enable, return from GFX hw_init to the device
phase2 dispatcher, SDMA3.1 initialization, remaining IP blocks. Later IB/fence
validation is distinct. Do not assume the next operation is an IB or that the
last printed queue marker identifies the faulting hardware engine.

Two small corrections exist in cached AMD source commit
5349075eac146ae0511d8929fc24451e4d9a4b7e and are absent from our6.12 source:

* Flush the initial posted scratch MMIO write with a readback before submitting
  the CP write. Otherwise the CPU write may arrive after the GPU write, yielding
  a false ring-test failure. Backport is in0014.
* Accumulate compute ring-test failures and return them. Original6.12 ignores
  their results and can report GFX initialization success despite a failed
  compute test. Backport is also in0014; this is truthful error propagation,
  not a fix for the PCIe hang itself.

Primary patch discussion for posted-write ordering:
https://mail-archive.com/amd-gfx@lists.freedesktop.org/msg154027.html
The compute-return change also appears in the June17 upstream amd-gfx submission:
https://www.mail-archive.com/search?f=1&l=amd-gfx%40lists.freedesktop.org&o=newest&q=date%3A20260617
Exact cached source, rather than the search index, is the comparison authority.

0015 records entry/result for ring-test helper calls, phase2 IP hw_init calls,
and the final gfx8 GUI-idle interrupt enable. Only Polaris11 emits these
markers. It adds no register probes, queue omissions, endian swaps or retries.
It distinguishes post-map GFX/KIQ/compute from SDMA/later IP execution. Logging
can alter timing and is diagnostic; success would not prove the previous cause.

## Boundary ledger

| Object | Current6.12 candidate contract | Review consequence |
| --- | --- | --- |
| GFX/KIQ/compute rings | Targeted software LE writer; matching hardware ring swap disabled | Retain the paired writer/control changes; no blanket extra swap |
| GFX/compute IB contents | Native CPU words; existing hardware IB endian control | Do not apply the ring encoder blindly to IBs |
| MQD backups vs GPU publication | Native backups, IO-safe LE publication;22 GPU samples measured | Samples narrow encoding errors but do not prove every field |
| SDMA ring/IB/read-pointer | Separate existing hardware swap controls | GFX ring experiments do not justify changing SDMA encoding |
| GPU writeback | Explicit LE decoding in calibration/SDMA helpers | Audit each consumer, not all PCI/MMIO globally |
| MMIO scratch initialization | Posted CPU write needs a readback before GPU submission |0014 imports the owning-boundary upstream correction |

A separate later-stage inconsistency was noted: gfx8 ring_test_ib reads its
WRITE_DATA result without le32_to_cpu while the SDMA test explicitly decodes
it. This needs validation against the actual packet/store contract before a
separate change; it does not explain the current pre-IB last-observed failure
and was deliberately not folded into this candidate.

## Build and exact resumption point

R730 workspace:
/srv/data1/tabor-build/linux-live-001/work/gfx-postmap-review-20261107-001
Inputs:
/home/owner/gfx-postmap-review-20261107

build.py verifies cached Debian6.12.113-1 source hashes and all13 parent patches,
extracts a fresh source tree, reapplies them and checks the three reviewed source
file hashes. Adds0014/0015, retains exact accepted config SHA
7effb33413cbb4ab6dcda93563c2600f1948f9764387df70cd016883892fdaec,
prepares fresh generated headers and copies Module.symvers from the matching
accepted build for unchanged kernel exports. No source tree or SDK is overwritten.

First invocation stopped before module compilation because relative M= was
interpreted as an external-module output path. This is a build invocation error,
not evidence of a C defect. resume.py uses the normal in-tree amdgpu.ko target.
The retained receipt/log records the failed attempt separately.

At errand breakpoint, container tabor-gfx-postmap-review-002 runs only the
isolated build,4 CPUs/6GiB/network-none. It writes build-002.log and
build-002.json and exits; it has no SSH credentials, device access, deployment
or follow-on hardware action. Inspect those outputs on return. If compiled,
verify ELF32 BE, vermagic6.12.113-tabor-modular, new module SHA and unresolved
symbol-version compatibility before staging anything to the board. Build
success is not hardware acceptance.

Next hardware work, only when resumed: one reviewed first bind, USB root
protected read-only, off-board logs and exact candidate verification. Do not
repeat a failed bind or unload/reload it. Decode the first unmatched INIT_TRACE
boundary before another code change. Until then the live board is untouched.
