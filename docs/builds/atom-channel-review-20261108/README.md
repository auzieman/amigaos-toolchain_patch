# Clock-channel correction and physical advancement — 2026-11-08

**The corrected AMDGPU module passes the previous DPM-enable failure on the physical A1222.** It then encounters a PCIe/machine-check failure during the UVD decoder ring test. No local console, scanout or acceleration is accepted.

This trial did **not** boot a newer kernel. The running kernel remained `6.12.113-tabor-modular`; only a matching experimental AMDGPU module was loaded from RAM. A separately built newer upstream kernel is a different experiment and is not validated by this result.

## Shared producer defect, before downstream SMU programming

The exact pinned `ppatomctrl.c` constructs the Polaris engine-clock request using:

```
pll_patameters.ulClock.ulClock = cpu_to_le32(clock_value);
pll_patameters.ulClock.ucPostDiv = COMPUTE_GPUCLK_INPUT_FLAG_SCLK;
```

`COMPUTE_MEMORY_ENGINE_PLL_PARAMETERS_V4` uses native 24-bit frequency and 8-bit flag C bitfields, with declarations reversed under ATOM_BIG_ENDIAN. The ATOM interpreter, however, reads its parameter space using get_unaligned_le32 and writes cpu_to_le32 words. Swapping an integer and then assigning it to a 24-bit bitfield truncates the swapped integer on BE; subsequently assigning the flag places it in the first memory byte rather than the LE word's high byte. Output extraction from those bitfields has the corresponding layout problem.

Compiled reproduction using the actual source type and input statements:

| Request in 10kHz units | Original x86 interpreter word | Original PPC interpreter word | Corrected PPC |
| --- | --- | --- | --- |
| 30000 (300MHz) | 01007530 | 00007501 | 01007530 |
| 100000 (1000MHz) | 010186a0 | 00018601 | 010186a0 |

The missing/misplaced flag matters independently of the numerical frequency error: it selects how ComputeMemoryEnginePLL interprets the input. A successfully returned ATOM invocation does not establish correct request semantics.

Patch0020 owns the repair in the ATOM parameter producer: serialize the **complete** LE word `(frequency & 0xffffff) | (flags << 24)` using put_unaligned_le32; decode the complete output with get_unaligned_le32 and masks/shifts. It covers the related VI/AI/Kong clock requests and AI memory timing input in this file. SI full-word input/output is explicitly checked unchanged. It does not alter global MMIO, PCIe, DMA or endian macros.

## Historical analogue and trace ledger

The Radeon Evergreen engine PLL path already combines clock and flags into `args.v3.ulClockParams` and converts the complete word. This is visible in both the pinned 6.12 source and [upstream Linux5.4 Radeon source](https://github.com/torvalds/linux/blob/v5.4/drivers/gpu/drm/radeon/radeon_atombios.c). This is a concrete older-driver implementation analogue; no assertion is made that we captured an old Tabor machine executing that exact branch. The vendor kit's radeon-enabled/amdgpu-disabled config and historical desktop reports remain separate evidence.

| Boundary | Writer → consumer | Required contract | Finding |
| --- | --- | --- | --- |
| ATOM clock parameters | ppatomctrl → atom.c parameter space | Full LE32 frequency/flags word | Corrected native bitfield truncation/layout |
| ATOM PLL results | Interpreter → ppatomctrl divider fields | Full LE32 word; LE16 divider fields | Clock-word output decoding corrected; existing LE16 decoding retained |
| Normal SCLK levels | polaris10_populate_single_graphic_level → byte uploader | Native divider values converted fieldwise to BE | Existing conversions retained |
| AVFS calibration levels | Static literals/VRConfig → byte uploader | Same BE wire bytes on every CPU | Patch0019 converts all multi-byte constants explicitly |
| SMU byte channel | smu7_copy_bytes_to_smc → indexed MMIO | Assemble input bytes MSB-first | Matches older Radeon ci_copy_bytes_to_smc; left unchanged |
| SMU commands | CPU-native message → register accessor | Native register value, normal Linux MMIO | Existing accessors retained |

AVFS calibration and regular SCLK-table preparation are different producers. Patch0019 makes the complete448-byte graphics array,24-byte memory record and4-byte VRConfig identical to their original x86 bytes. Byte fields are preserved. BootMVdd already used the standard conversion and remains unchanged.

## Candidate and validation

Parent module7067488b and its source/output remain preserved. `stage.json` pins the fresh candidate source hashes and ordered additional patches0018,0019,0020,0021. Patch0018 propagates mandatory table/start errors;0021 records actual ATOM inputs/dividers and existing AVFS gate values without extra hardware reads. Neither substitutes success for failed hardware.

- Source-derived calibration objects compiled with native GCC and PPC GCC; all476 compared bytes match original x86. Original PPC objects differ. Exact hashes in tests.json.
- Actual AI input statements compiled and executed natively and under qemu-ppc for10 frequencies. Corrected PPC/x86 words agree; original PPC differs. Output helper frequency/flag extraction also checked. The fixture models unaligned byte helpers and directly extracts the real type/statements; it does not execute a complete VBIOS interpreter or physical MMIO.
- First Kbuild attempt rejected a patch-generator substring match in an unrelated SI routine. Its failed log and stage hashes are retained. Token-boundary matching plus an unchanged-SI assertion corrected the generator; a fresh candidate002 was prepared from the preserved parent.
- Normal Kbuild modules completed exit0, GCC14.2.0-19/binutils2.44, pinned image2781e118,4 CPUs/6GiB, network disabled. No toolchain copied or downloaded. ELF32-BE/module vermagic and all687 import CRCs match the running kernel reference.
- Candidate SHA256: `44823d09a89db4ef83c124854008285ae2cb62cf4766d2a029e9d30080d722b0`.

## Physical outcome

One fresh first bind, candidate and sshd logs in RAM, verified read-only USB root and off-board /dev/kmsg capture. Kernel6.12.113-tabor-modular, RX560/Baffin1002:67ff. No boot script, kernel image, default module or filesystem deployment changed.

- AVFS efuse49=`0004dfc3`, feature mask=`fff73fdf`, cold SMU start (`smc_running=0`), avfs_supported=1, btc=0, event_result=0. This closes the earlier uncertainty: calibration **was executed** in this trial, though BTC itself was not requested.
- Recorded clock requests carry the correct SCLK flag; for example21400 → request01005398, with returned fcw_int34/fcw_frac15728/pll_range0.
- DPM_Enable0x14e responds1 in5825us. smu7_start_dpm, complete PowerPlay hw_init and DCE hw_init return0. The previous DPM failure is passed.
- First observed PCIe fault now follows entry to UVD ring testing,404035us after the successful DPM acknowledgement. The later UVD odd-NOP warning is after the first machine-check/PCIe report and is not assumed to be the cause. SSH connection drops; no repeated bind or hardware probing afterward.
- Both serialization fixes were present: this trial does not isolate which repair, or their combination, removed the old DPM failure.

Exact events: hardware-summary.json. Raw logs, read-only mount proof, stages and failed-bind receipt: hardware-offboard-001/. A passing DCE hw_init alone does not prove a framebuffer exists or the display works.

## Next bounded gate

Review UVD startup/ring submission before the first register test, retaining its existing explicit BE RB/IB swap controls. Do not globally convert its packets on the strength of the earlier ATOM defect. Its ring-pointer warning may be a consequence of the preceding bus fault. A diagnostic using the standard IP-block mask could separately isolate optional codecs from display acceptance, but no such mask or permanent feature removal was applied here. Any future first-bind requires a fresh hardware boot after this failed trial.
