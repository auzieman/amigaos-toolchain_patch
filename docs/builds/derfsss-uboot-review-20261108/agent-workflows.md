# Agent workflow intake

Reviewed pinned MCP-AmigaOS4 b5f1efa9cb3206340c58860382c178c0c0a9898e:
- AGENTS_SETUP.md: environment/config/capability validation and client wiring.
- host/src/amiga_fleet_mcp/prompts.py: eight named workflow templates
  (getting_started, investigate_crash, deploy_and_run, check_fleet, safe_reboot,
  deploy_library, run_test_batch, ab_test_fix).
- INSTALL.md, USAGE.md and SECURITY.md as deployment/tool-contract context.

Reviewed pinned qemu-runner bb727303c992038351c84b6f3b56a09d9a104ce2:
- README.md, dev_cycle.py and test_runner.py.
- No AGENTS.md/CLAUDE.md/SKILL.md or prompt file was found in this revision's
  complete recursive tree. Its operational knowledge is in code/docstrings and
  README. dev_cycle.py still has Windows-centric default paths; test_runner.py
  has WSL commands and unbounded make nproc. Do not execute those defaults here.

The MCP prompt definitions explain job continuation rather than duplicate
execution, version-in-memory versus on-disk checks, alert interpretation,
non-wrapping debug ring limits, preserving logs and controlled A-B tests.
These are useful engineering workflow references, not Linux Polaris fixes.
No upstream installation or reboot instructions were executed during intake.
Adapted in .agents/prompts/amigaos-evidence-cycle.md in original local wording;
no upstream code or skill was installed. MCP tool names describe that project's
API and do not imply those tools are available in this Codex session.

Source links:
https://github.com/derfsss/MCP-AmigaOS4/blob/b5f1efa9cb3206340c58860382c178c0c0a9898e/AGENTS_SETUP.md
https://github.com/derfsss/MCP-AmigaOS4/blob/b5f1efa9cb3206340c58860382c178c0c0a9898e/host/src/amiga_fleet_mcp/prompts.py
https://github.com/derfsss/qemu-runner/blob/bb727303c992038351c84b6f3b56a09d9a104ce2/dev_cycle.py
https://github.com/derfsss/qemu-runner/blob/bb727303c992038351c84b6f3b56a09d9a104ce2/test_runner.py
