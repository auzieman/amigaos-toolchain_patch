# Connected native-state to device-table regression

The old tests supplied independent native clocks to table construction. They
could pass while the actual raw-state constructor supplied byte-reversed
clocks. This regression connects those stages using their actual source
functions, with separate translation units preserving each fixture's private
mock structures.

`test_connected.py` runs on the R730 only, bounded to one CPU and 6GiB. It
consumes the source fixtures from state-clock-decode-20261108,
clock-table-pipeline-20261108 and smu-flow-review-20261108. Run the aggregate
preflight first to regenerate those inputs. Generated source hashes and output
hash are retained in receipt.json; full generated sources and binaries remain
under /srv/data1/tabor-build/source-review/connected-gpu-flow-20261108.

The connected path uses ten actual driver functions:

1. V1 raw PowerPlay state constructor (both revisions).
2. DPM state clock update and engine/memory trimming.
3. ATOM divider request/response and Polaris SCLK calculation.
4. Complete individual graphics and memory level construction.
5. Indexed SRAM upload.
6. Parameterized SMU sender and response-status handling.

All 72 revision/index-range cases pass on fixed x86 and QEMU PPC32 BE; all
53,883 emitted bytes match unchanged old x86. Each accepted case builds and
checks eight graphics/memory level pairs and submits its generated SCLK mask
against six modeled response classes: 432 mailbox checks per architecture.
Both engine and memory masks must equal the selected range. Only the SCLK
mask is submitted; no MCLK command sequencing is modeled.

Old PPC reproduces corrupt native clocks and all 72 cases are rejected by an
offline domain guard before upload or message submission. This guard is test
instrumentation, not a new driver bypass or a claim that runtime validation
fixes the source bug. Patch0024 remains the actual constructor correction.

The raw state indices, voltage/profile inputs and several ATOM response fields
are synthetic. Four PLL reply fields per clock come from the physical logs.
This exercises complete individual level objects, not a complete DPM table or
hardware initialization. Numeric register mocks cannot validate DMA,
coherency, timing, firmware execution or display output. The SRAM interface
still uses its documented MSB-first bytes, ATOM uses LE words, and native
clock values remain native between boundaries.

All eight aggregate suites pass. The overall hardware/deployment gate remains
BLOCKED because the missing captured contracts remain unresolved. The USB was
not mounted or written, no GPU was accessed, and e2e-004 remains uninstalled.
