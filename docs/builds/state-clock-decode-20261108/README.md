# Native power-state clock decoding boundary

A whole-flow review found a direct match to the later physical anomaly, upstream of the final SMU message. e2e-003 kmsg records an ATOM clock request2555576320(0x98530000), exactly bswap32(21400/0x00005398). The shared clock encoder masks this oversized input into request01530000; captured output is fcw_int0/fcw_frac0/pll_range4/ssc0. The later clock-mask transition faults. These exact captured fields are retained in ../clock-table-pipeline-20261108/partial-physical-inputs.json.

## Producer and propagation

smu7_get_pp_table_entry_callback_func_v1 directly loads raw little-endian ulMclk/ulSclk into native performance-level clocks. Both low/high MCLK loads and both low/high SCLK loads for each of Tonga/Polaris revisions lack decoding: six raw loads at one V1 state-construction boundary. The separate dependency-table parser already decodes its clocks, so source can hold correct native dependency arrays alongside incorrect native requested states.

smu7_find_dpm_states_clocks_in_dpm_table compares the malformed requested clock with the correct native DPM array. If the request is larger than the last supported level, it overwrites the highest table entry and requests a table rebuild. smu7_trim_single_dpm_states then selects levels using the malformed bounds. This explains how a representation error can propagate into both a rebuilt clock object and the later mask, without the mailbox serializer being broken.

Candidate0024 applies existing le32_to_cpu to all six raw clock loads at this boundary. No changed message constant, forced0xffmask, frequency normalization, GPU workaround or mailbox swap. This is not a claim that all driver interfaces or older V0 state parsing are repaired.

## Connected regression

The standalone test extracts the actual V1 constructor, DPM update and trimming routines, with actual packed VBIOS table declarations. It tests both dependency revisions and every low/high index pair among eight entries:72scenarios per old/candidate and x86/PPC combination,288total. It checks engine AND memory clocks, highest-entry preservation, and resulting masks. PCI capability helpers and final mask aggregation are modeled; these do not determine clock byte decoding.

Original PPC with a valid raw21400clock state produces98530000, overwrites the final SCLK entry with it, and yields mask80—matching the physical clock/mask signature. Candidate PPC matches unchanged x86 across the complete test output. Corrected states keep native clocks and the supported DPM arrays unchanged; expected masks depend on the actual selected range, not a universalff.

This establishes a source defect and reproduces its propagation with constructed raw VBIOS states. The actual physical selected state blob/indices were not captured, so exact physical causal attribution remains unisolated. Candidate patch apply-check passes against e2e-003; no kernel compile, deployment, GPU access or hardware trial occurred for0024.

The aggregate preflight now runs seven suites, all passing, but remains BLOCKED/deployment_allowed=false for uncaptured complete firmware/table state and physical semantics. A passing negative-control test of the old defect is not acceptance of the installed e2e-003 driver.
