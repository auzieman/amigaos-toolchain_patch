# Pre-hardware oracle for the VM page-table encode path (2026-11-24)

`harness.py` extracts the real `amdgpu_vm_sdma_update`, `amdgpu_vm_sdma_copy_ptes`,
`amdgpu_vm_sdma_set_ptes`, `amdgpu_vm_map_gart` and `sdma_v3_0_vm_{copy_pte,write_pte,set_pte_pde}`.
The old version comes from vanilla v6.12.113, the new one from kernel 021. Each is built for
x86-64 and for ppc32 (run under qemu-ppc).

A model of the SDMA v3 engine executes each IB as the hardware sees it on that host:
- command dwords are the CPU-native words (hardware IB swap on BE);
- COPY_LINEAR data are raw bytes (swap 0).
The page table is kept as LE GPU memory. The job allocator mirrors `amdgpu_vm_sdma_alloc_job`:
256 dw from `prepare`, plus 2 per PTE on the copy path, capped at 16K. So a 2 MiB mapping
splits across two SDMA jobs exactly as in the kernel.

Cases:
- a 2 MiB GTT BO (512 scattered pages, some above 4 GiB, a high flag bit; copy path);
- a contiguous VRAM range (GEN_PTEPDE);
- a 2-entry update (WRITE).

Run on the R730 with `python3 harness.py <v6.12.113 tree> <021 tree> <workdir>`.

Result: **PASS** (`results/`). new-ppc == x86 for every entry: 0 of 512 GTT entries wrong. That
includes entry 16 (VA 0x210000, glamor's IB page), the split across two jobs and the high-dword
pages. The VRAM and WRITE cases are identical too. old-ppc (vanilla) writes all 512 GTT entries
byte-reversed (`7300001000004000` for `0040000010000073`), which confirms that our 9-line
`cpu_to_le64` change in `amdgpu_vm_sdma.c` is required and correct.

A harness bug found on the way: a fixed 96-dword IB stub overflowed. The kernel keeps its local
`ndw` across a job re-allocation, and that is safe only because the real allocator sizes each
IB for `count`. The stub now mirrors the real sizing.

**Limits:**
- This models the SDMA v3 swap semantics (command fetch swapped, copy data raw) as the earlier
  vm-pte-contract work established them; it does not re-prove them on hardware.
- The walker (`amdgpu_vm_ptes_update`) and the PDE levels above the PT are not exercised.
