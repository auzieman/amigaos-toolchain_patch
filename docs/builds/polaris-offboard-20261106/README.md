# Off-board first-bind capture

Fresh board SSH6.12.113-tabor-modular, no modules. Helper
scripts/test-polaris-offboard.py verifies board IDs and module hash, starts live
/dev/kmsg SSH stream to laptop, confirms marker before driver stages, and keeps
stage return codes/stdout outside the target filesystem. Process groups/timeouts
bound SSH/proxy cleanup. Syntax checked and physically executed.

Attempt001 stopped before any module load: root read-only remount busy.
Open-FD inspection identifies /tmp/sshd.log on USB, held by SSH listener/children.
Started diagnostic SSH2222 with log /dev/null, verified access; stopped original
listener102 and restarted normal22 with identical config/log /dev/null and PID
file in /dev. Verified normal access, synced and remounted root read-only. No SSH
configuration or boot defaults changed; runtime listeners reset on next boot.

Attempt002 successfully verifies capture and ro root, holds PCI match, resolves
dependencies via never-bound original, removes it and inserts candidate while
held. These stages all return0. Override cleared; explicit bind times out40s.
Board loses SSH; saved stream survives locally through kernel seq713.
SMU protected startup returns response1/status3. GFX CP setup completes; first
PCIe error starts~57.6ms after CP-start log. Repeated ERR_DR00800000,
CAP_STAT23/R0-R3zero, plus later SMU ret65535 messages. No normal ring-test pass
or display acceptance logged in this run. Previous GFX-only pass is separate.

Earlier in sw_init a PowerPC alignment warning occurs at memset+60, called from
gfx_v8_0_sw_init; source line1356 clears the BO-mapped MEC HPD/EOP area with
normal memset. Further symbol/source qualification required before declaring
this warning causal or replacing I/O accesses.

NXP primary background: same P1022 ERR_DR00800000 plus hangs is reported at
https://community.nxp.com/t5/PowerQUICC-Processors/P1022-Console-hangs-after-PCIE-error-dump/m-p/1364368/highlight/true
A separate P1022 endpoint case was traced to invalid SDK register accesses at
https://community.nxp.com/t5/PowerQUICC-Processors/P1022-PCIEs-error-detected-console-throws-continuous-error/td-p/1456944
Different endpoint/capture values; this does not prove our offending access.
Do not decode the vendor register using generic PCI AER masks or suppress errors
as a graphics fix. Next candidate adds a normal KIQ self-test before queue mapping
so packet execution and GPU MQD consumption become separate acceptance gates.
