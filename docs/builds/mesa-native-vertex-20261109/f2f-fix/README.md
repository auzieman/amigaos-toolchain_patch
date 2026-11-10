# Provisional vertex-format contract correction

## Actual producer/consumer failure

Kernel014 physical RGB stderr and retained earlier no-op runs report ACO rejecting
f2f32 and an undefined position export. Isolated SPE diagnostic run020 identifies
source_bits=8 from load_buffer_amd. Run021 follows actual producer/key/consumer:
valid R32G32_FLOAT producer emits raw90/log_size2, but an earlier provisional
variant has raw00/log_size0. Our patch0012 globally forced native decoding in
load_vs_input_from_vertex_buffer even for that unpopulated shader key. Zero
metadata was misinterpreted as an8-bit float, creating unsupported f2f32.

## Fix

Remove the unconditional environment-option trigger at this consumer. The
existing si_create_vertex_elements producer already enables opencode and retains
complete format metadata when the native contract is enabled. The populated
shader key therefore selects conversion. Provisional neutral-key variants keep
the upstream typed-load path. No ACO fallback, fabricated format, error bypass or
hardware operation was added. All temporary compiler/format diagnostics removed
from final source. Ordered follow-up patch0014 applies after the retained0012
candidate; earlier records are preserved rather than rewritten.

## Validation and limits

Private R730 source/build, accepted SPE SDK8.5, pinned tooling image,2CPUs/4GiB,
shared SDK/stage read-only. Clean full incremental build/install passes. Actual
SPE/QEMU runs023RGB and024attribute-free point have no ACO/undefined-value errors;
compiler-log gate rejects old020 and accepts023/024. No-op pixel failures remain
expected, because this backend executes no GPU. Temporary018run failed QEMU env
comma parsing before application;019 reproduced with valid flag. First private
build missed spe-cross.ini and failed; copied accepted config before successful
bounded builds. These were qualification setup failures, not GPU results.

CRITICAL: final selected executable uploads in023 and024 are byte-identical to
baseline016/017 respectively. The invalid provisional variant was not among those
uploaded executables. This is a proven own-patch compiler correction, NOT a
proven fix for the hardware hang. Prior constructor/byte-comparison acceptance
missed compiler diagnostics and is insufficient as compiler qualification.
The failure remains open; repeating a physical test solely for this change is
not justified by changed executable bytes. No board deployment/test this pass.

Source hashes, clean library hash, upload comparison, raw compiler traces and
resource launch evidence retained here. Diagnostic sources live only in the
private f2f-contract work tree; final source differs from parent only by this fix.
