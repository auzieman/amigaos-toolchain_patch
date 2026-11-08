# Whole SMU state-flow review

Scope reset: follow the complete data lifecycle rather than swap the next failing message. Source is the exact e2e-003 tree; no new driver patch, deployment or physical retry was made here.

flow.json retains85 source functions reachable by direct calls from the selected initialization/table/state/mask/transport roots across seven files, with definition locations, hashes and unresolved macro/external calls. flow-source.c.txt retains those actual function bodies. polaris-callbacks.json identifies the selected hardware implementation for virtual SMU operations. The graph is a review aid, not proof that every callback branch executed or that every field is correct.

## Owning boundaries

| Stage | Representation and conversion owner | Acceptance |
| --- | --- | --- |
| VBIOS power tables -> native clock/voltage dependencies | LE table fields decoded by process_pptables_v1_0 | Selected source pinned; full current table output not captured |
| Native clock request -> ATOM -> native divider result | Complete clock words use shared LE helper; other divider fields have typed decoding | Earlier actual CPU tests pass; complete hardware responses not retained |
| Native divider/dependency/profile -> GraphicsLevel and MemoryLevel | Polaris population functions construct native values then explicit HOST_TO_SMC conversion | Whole-object output parity still requires validation |
| Encoded SMC table -> SRAM | smu7_copy_bytes_to_smc packs bytes MSB-first into numeric register writes |256 upload cases per architecture preserve every source byte and untouched tail |
| State change | Find clocks -> optional link request -> freeze -> populate/upload -> AVFS update -> generate masks -> threshold -> unfreeze -> upload masks -> display notification -> optional link completion | Actual source order retained; exact branch and complete transient state not captured |
| Native enable mask -> mailbox argument/message | Common parameter sender uses numeric register accessors |255 masks x6response values per architecture pass unchanged |
| Mailbox response -> status -> caller | Common sender translates firmware status into errno | Six response classes pass; caller propagation must be audited across flow |

The table's SMC serialization and the register accessor's bus representation are distinct boundaries. A mask such as0x80 is a native numeric argument; inserting cpu_to_le32 before its already endian-aware register accessor would change the value on BE. No such swap is proposed.

## Executable tests

Three actual common transport functions are extracted: SRAM copy, message sender and parameterized message sender. Simulated SRAM/indexed-register endpoint captures the transfer. On both native x86 and emulated BE PPC:

-256 transfers: lengths1..64 at four aligned starts; all bytes inside and outside the write checked, including partial-word preservation.
-1530 request/response cases: masks1..255 against success, unsupported, all-ones, zero and other errors.
-Two alignment/limit rejection cases.

All1788 cases per architecture pass with identical output. This demonstrates host-independent transport behavior given the same encoded input; it does not validate actual firmware semantics, hardware timing, PCIe coherency or the table builder's inputs. The modeled wait returns immediately; real timeout/liveness is not simulated. Register bus accessors are outside this freestanding mock.

## Review findings and remaining work

The physical e2e-003 trace passes both encoder rings and all logged hardware-init blocks. First fault is47,539us after SCLKDPM_SetEnabledMask0x145/argument0x80 entry. Multiple state/force-level callers can emit that command; the trace does not identify which caller or establish that its argument was malformed. The observedffff response occurs after the PCIe fault and must not be interpreted as a normal firmware response.

The selected state transition explicitly repopulates/uploads clock levels before enabling their mask. It is therefore insufficient to validate only the final message. Compare the COMPLETE native dependencies, ATOM divider outputs, encoded GraphicsLevel/MemoryLevel/link entries and mask bounds through this transition. Track which shadow objects are native versus already encoded and audit all writers/readers for repeat conversion or stale values. No further physical command trial is justified by this transport-only test.

Caller error propagation is also incomplete in source: smu7_upload_dpm_level_enable_mask ignores message results and returns0; smu7_set_power_state_tasks records errors but continues through later stages. These are flow-level recovery concerns, not established first-fault causes. Do not turn them into an isolated alleged hardware fix or claim success because a wrapper returned0.
