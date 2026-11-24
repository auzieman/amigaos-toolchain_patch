# Pre-hardware oracle for patches 0040 and 0041

`harness.py` extracts the real driver functions from the kernel 021 tree (old) and the
0040/0041 tree (new). It compiles them against the real `atombios.h`/`pptable.h` for x86-64
and for big-endian ppc32. The ppc32 builds run under `qemu-ppc` on the R730.

The binaries are freestanding: the build host has no ppc32 libc, so printf is a small
built-in over raw `write(2)`. Inputs are byte-identical LE data:
- an ASIC_ProfilingInfo v2.1 table and a GFX_Info v2.3 table (in 64 KiB images, so a
  byte-swapped u16 offset still lands inside, as it would in a real VBIOS);
- UVD create/decode/destroy messages;
- a VBIOS stand-in that reads and writes its parameter space as LE bytes.

Outputs are the values the driver derives, plus the bytes the VBIOS or encoder sees.

Oracle per test: old-x86 == new-x86, new-ppc == x86, and old-ppc != x86 (proves the test
reaches the bug). Run on the R730 with
`python3 harness.py <021 source> <patched source> <workdir>`.

Result (2026-11-24): all three PASS (`results/receipt.json`, per-binary logs in `results/`).

| Function(s) | old ppc | new ppc = x86 |
|---|---|---|
| `atomctrl_get_leakage_vddc_base_on_leakage` | VDDC/VDDCI 0 for every level (swapped offsets miss the arrays) | 900-950 / 800-850 mV |
| `atomctrl_get_leakage_id_from_efuse` | 0x2301 | 0x0123 |
| `atomctrl_get_voltage_evv` | VBIOS receives id `01ff`, gives 7 mV | `ff01`, 1150 mV |
| `atomctrl_get_edc_hilo_leakage_offset_table` | 0x3412 / 0x4000 / 0x8000 | 0x1234 / 0x0040 / 0x0080 |
| `atomctrl_get_edc_leakage_table` | DIDT values byte-swapped | correct |
| `amdgpu_uvd_cs_msg` (+ `_decode`) | decode rejected: "Illegal UVD message type (16777216)"; handle 0x34120000 never freed | decode accepted, buffer sizes computed, handle 0x1234 freed on destroy |
| `uvd_v6_0_enc_get_create/destroy_msg` | IB fetched as native words (`00000018 ...`) | LE (`18000000 ...`), byte-identical to x86 |

**Limits:**
- This validates representation only. The VBIOS and the encoder firmware are modelled as
  LE consumers with no hardware swap. For the encoder IB that assumption follows 0023 and
  VCE; it is not yet shown on hardware.
- Not exercised: the `process_pptables_v1_0` boost limit, the `amdgpu_atombios` firmware
  VRAM reserve and the `atom.c` version chain. Each is a one-line decode of the same form.
- The EDC test output also shows the upstream `get_edc_leakage_table` behaviour (it reads
  from the GFX_Info base, not base + offset). That is unchanged by these patches.
