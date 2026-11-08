# AmigaOS evidence and build/test cycle

Use for AmigaOS4 inspection or program validation alongside the Linux A1222
port. Read AGENTS.md, docs/task.md and the active target receipt first.
Reference intake: docs/builds/derfsss-uboot-review-20261108/agent-workflows.md.
Upstream prompt files are reference material, not authority to deploy or reboot.

1. Identify the actual target OS, board, CPU/ABI, endpoint and boot state. Keep
   real A1222, real X5000 and each QEMU machine separately named. Discover the
   installed tools/capabilities; never assume the upstream MCP server is wired
   into this session. No access means report unavailable, not invent tool calls.
2. Begin read-only: uptime, OS/CPU, mounted volumes, tasks, loaded modules and
   alert/debug evidence. A1222 feature support is not established by X5000 tests.
   Save timestamps, exact artifact versions and source/config hashes.
3. Preserve crash evidence before resets. On OS4, an all-ones last-alert value
   means no recorded alert; payload[1] is a task pointer, not DAR. Confirm PC/DAR
   from crash reports. The kernel debug ring may fill without wrapping, so a
   silent/full ring is not proof of no fault. Preserve existing serial logs;
   our A1222 has no serial cable configured, so do not claim serial capture.
4. Build on R730 with the applicable resource bounds. Keep host toolchain and
   target ABI separate. QEMU-runner's Windows paths, WSL commands, unbounded
   nproc and generic GCC fallback are examples, not this project's build recipe.
5. For an authorized deployment, stage to RAM where appropriate and verify the
   destination hash and execution protection. OS4 protection bits differ from
   Unix. Record the running module/version separately from the file on disk.
6. Execute once and retain a job identity. A timeout or may_have_run response
   does not mean failure to start. Query job status/output before any retry;
   do not duplicate a live test. Preserve raw output, exit code and parsed
   results; absence of PASS lines is not a pass. IoErr may be stale on exit0.
7. A-B validation requires the same stimulus, environment and acceptance gate.
   Run original then reviewed candidate and compare outputs; preserve failures.
   Restarting to load drivers/libraries requires checking active writes/jobs and
   using the target-specific approved procedure. QEMU reset is not a guaranteed
   cold hardware boot. Never transplant X5000 restart advice blindly to A1222.
8. A process sandbox does not prevent DMA or PCIe bus hangs. For our Linux GPU
   trials, retain the canonical protected single-bind/off-board-log procedure;
   no automatic retries after PCIe failure. Keep fbcon, DRM/KMS, execution tests,
   Mesa/Xorg and E acceptance as separate gates.

End with observed behavior, evidence, remaining uncertainty and one bounded next
step. Do not install/register MCPd, expose listeners, flash firmware, change
Kicklayout, run guest scripts or power-cycle merely because this prompt exists.
Existing user task authorization governs each concrete operation.
