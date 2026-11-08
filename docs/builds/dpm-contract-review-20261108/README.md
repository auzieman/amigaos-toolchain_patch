# DPM contract review — 2026-11-08

Review uses the pinned7067488b hardware candidate and off-board trace, plus the
new OS4 evidence-cycle workflow. No driver bind, reset or firmware change.

## What the trace actually narrows

smu7_start_dpm -> smu7_enable_sclk_mclk_dpm first sends PPSMC_MSG_DPM_Enable
(0x14e) for SCLK. The first PCIe fault occurs45,333us after that entry. MCLKDPM
and PCIeDPM enable commands occur later in this function and were not reached
before the initiating error. Later0xffff mailbox results are downstream of
PCIe failure, not independent proof of corrupt command byte order.

The Polaris table producer serializes graphics clock frequency/PLL fields with
HOST_TO_SMC macros (cpu_to_be32/16). Link-level fields include byte-sized speed
and lane codes, BE up/down thresholds. Each GraphicsLevel also has a byte
pcieDpmLevel index. Therefore SCLK activation can consume linked state; its
position before explicit PCIeDPM_Enable does not exclude a PCIe interaction.
No table byte-order violation has been proven by this pass. Outbound bridge
maps were previously matched against derfsss U-Boot and historical DTS.

## Rejected lead

polaris10_populate_single_graphic_level overwrites the result of
polaris10_calculate_sclk_params, but the latter returns0 after both the ATOM
success path and intentional arithmetic fallback. A discarded draft checked
this value; it is not an established error or included in the retained patch.

## Real error-flow correction, not a bus repair

Experiment0018 changes smu7_enable_dpm_tasks to return immediately if
smum_init_smc_table or smu7_start_dpm fails. The existing routine stores errors,
continues later SMU operations and returns0. Physical trace shows start_dpm
returning-22 and subsequent commands after the bus fault. Optional feature
handling stays unchanged. This prevents masking/cascading those prerequisite
errors; it cannot reverse PCIe loss or prove why DPM_Enable failed.

prepare.py reproducibly emits the patch from the pinned source without
modifying it. git apply --check exits0. test_errors.py extracts the actual
original/modified startup routine and compiles a native fault-injection test on
R730 with stubbed hardware helpers. It demonstrates original return0 + later
calls for injected table/start errors, corrected-5/-22 + no later calls, and a
successful path that still runs later calls. This is control-flow validation,
not kernel compilation, BE serialization validation or hardware acceptance.
The first native test compile lacked a PPSMC_Msg stub typedef; corrected fixture
passes. No driver build or physical fix is claimed.

## Bounded next hardware/source experiment

Before another bind, retain actual effective PP feature mask and dump decoded
SCLK/voltage/PLL plus linked PCIe levels at the producer boundary. Check counts,
indices, host capability clamping and SMC SRAM copy/readback against exact
structure offsets. Review all writers before changing serialization.
A candidate using the existing PP_SCLK_DPM_MASK mechanism can isolate SCLK
transition from broad amdgpu.dpm=0, but must preserve/record all other effective
feature bits and requalify CRC/vermagic. This is a proposed controlled test,
not an already-built workaround. Do not repeat7067488b or infer a new card fix.
