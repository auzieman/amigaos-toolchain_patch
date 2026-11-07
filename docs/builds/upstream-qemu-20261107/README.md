# Upstream7.3 QEMU runtime gate — 2026-11-07

From clean AMDGPU GitLab5349075, added only a QEMU config variant: PPC_QEMU_E500,
SERIAL_OF_PLATFORM and virtual PCI block/network/RNG support. Source mounted
read-only; output copied from the accepted clean7.3 build, preserving hardware
outputs. Standard Kbuild vmlinux completed exit0. Distinct release
7.3.0-rc6-tabor-upstream-qemu-001; exact kernel hash in runtime receipts.

Tests use native QEMU10.0.13 ppce500/e500v2 TCG, no network,1GiB guest RAM,
2CPU/2GiB server cgroup, disposable disk snapshots. Original rescue disk hashes
match before/after each run. These are not physical Radeon tests. The root is
the preexisting static rescue, not a package-managed Trixie installation.
Its ABI binary matches prior retained SHA793736ab53f0d5dcd08c35f066da65597955f957bb9a97fd6b8f6258594b1265
and its ELF comment reports GCC8.5. No GCC14 SPE userspace acceptance.

- Two CPUs: stopped at secondary startup, never reached shell within150s.
- One CPU: shell and commands execute under the expected new kernel;8/9 ABI
  checks pass. fenv remains FAIL (exit1), so overall runtime acceptance fails.
  Six software/SPE fractal trials produce equal12288-byte images and expected
  checksum2882920052. Timings are emulator evidence, not hardware benchmarks.
- Two CPUs with temporary nosmap: also stalls during secondary startup within90s.
  KUAP activation differs from the old working QEMU config, but this negative
  control does not establish it as the cause. Do not carry nosmap to hardware.

The last visible message is not sufficient to locate the stalled operation.
Next bracket secondary CPU entry/release/ack against the older working QEMU
kernel and its config, or compare a qualified newer emulator. No further
speculative config change or physical reboot performed.

User authorizes matching hardware USB update if this test works. Hardware
payload is packaged and staged inactive on the live A1222; active boot files
were not switched because dual-core boot remains unresolved. The preexisting
fenv failure is separate from that pre-userspace SMP startup gate.
