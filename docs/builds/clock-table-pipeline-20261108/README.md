# Connected clock-level byte pipeline

Five actual pinned production functions run together: ATOM engine-divider decoding, Polaris PLL calculation, complete graphics-level construction, complete memory-level construction and SRAM upload. Actual packed SMU level declarations and pp_endian.h conversions are used.

256scenarios per native x86/BE-PPC architecture vary eight captured valid clocks, native/OD dependency selection, deep-sleep policy, hysteresis overrides and ATOM success/fallback. Complete GraphicsLevel56-byte and MemoryLevel24-byte objects match across architectures:20480bytes per run. Decoded semantic fields and byte-preserving SRAM upload are independently checked.

Four ATOM result fields per clock use actual physical log values: FCW integer/fraction, PLL range and SSC enable. Other response fields, voltage dependency results, profiles/display inputs, sleep-divider helper and SRAM endpoint are deterministic synthetic inputs, explicitly identified. These tests do not qualify the physical firmware table, voltage dependencies or a full DPM table.

The physical input extractor also found a ninth request outside the24-bit clock domain:98530000, the byte reversal of valid5398. It is retained as an anomaly, not silently normalized or included among the eight valid replay inputs. This led upstream to the state-construction defect documented in ../state-clock-decode-20261108/.

The aggregate preflight includes this test and the connected state-decoding regression. No new hardware access or deployment. Full physical input capture and complete-table qualification remain open.
