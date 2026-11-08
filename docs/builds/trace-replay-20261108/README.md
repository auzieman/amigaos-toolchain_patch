# Capture-backed shared-codec preflight

The wrapper experiments passed real targeted ATOM/UVD gates, but a later timeout is not proof of another untranslated interface. This slice adds real x86-capture replay and one aggregate gate before further patches or deployment.

## Captured reference

Pinned trace SHA2bbfff70d4419797e22b0e121d0672f2dd237aa410202687e6c639b16a65a3ac,190962selected register events,75SMU message transactions. All75have an observed nonzero response. The parser retains message/optional argument/first response and transaction order. It never fills a missing response with success. This is six filtered numeric register offsets, not a complete bus/command-buffer trace. Missing trace loss statistics mean completeness is not established merely by parsing all recorded messages.

The retained x86 capture is kernel6.12.94+deb13-amd64; the target is6.12.113-tabor-e2e-003. Same card does not imply identical requested policy, DMA addresses or branch execution.

## Replay

The actual common SMU parameter/message sender functions run in freestanding native x86 and BE-PPC executables against an endpoint using the75captured transactions/responses. Message, optional argument and decoded return status are checked in order. Outputs match exactly. The endpoint uses numeric register values as the kernel accessor interface supplies; it does not test readl/writel bus transactions, polling counts, timing, firmware execution or construction of the caller's tables.

The x86 trace's five SCLKDPM_SetEnabledMask0x145 transactions all pass argument0xff and return1. PPC's later fault follows argument0x80. These are different selection masks, not direct evidence of byte reversal. Source has several possible mask callers. Before a new conversion, establish the actual caller and full level-table state. Never force PPC to0xff merely to match a trace collected under different inputs.

## One preflight entrypoint

On R730: python3 /home/owner/preflight-gpu-codecs.py

This script runs actual-source ATOM, common ring, UVD encoder, SMU transport and capture replay suites serially, pinned to one available CPU and6GiB address space. All five pass. The overall report remains BLOCKED/deployment_allowed=false and exits2 because complete input/table/firmware-state coverage is missing. This exit is intentional; five green subset suites must not be interpreted as a complete GPU qualification.

Required next coverage: native clock/voltage dependencies -> actual ATOM divider outputs -> complete serialized clock/memory/link table objects -> uploaded bytes -> generated masks -> captured firmware response and error propagation. Use software extraction/replay first, account for every representation's writer and reader, and report missing inputs rather than manufacture known-good data.

No new kernel patch, boot-file change, hardware access or GPU retry occurred here. No claim of a complete simulator or whole-driver fix. See preflight.json, receipt.json, transactions.json and ppc-observations.json.

Follow-up: aggregate entrypoint now includes connected complete-level construction and native V1 state-decoding regression (seven suites). All pass but gate remains blocked. The observed reversed clock was traced to six raw VBIOS clock loads in state construction; actual-source propagation reproduces highest-entry overwrite and mask80. See ../state-clock-decode-20261108/. No final-message swap is required by this evidence.
