# E guest log review — 2026-10-31

Read-only review of software-e003. E redirects stdout/stderr to
/home/tabor/.e-log.log (and rotates .old); /tmp/e-session.log alone misses E's
main messages. Summary contains exact normalized messages/counts and raw input
hashes. Raw snapshots are retained locally at work/e-log-review and the running
guest retains its logs. No guest configuration, media or privileges changed.

- Four module-load errors: lokker, mixer, music-control, polkit. The selected
  build deliberately disables them, but the upstream standard profile still
  requests them. Align a minimal profile with compiled modules rather than
  treating these as compiler or QEMU CPU failures.
- E_SUID_ERR: Unable to assume root user privileges. The stager preserves only
  ordinary executable permissions. The source's e_system.c maps inability to
  become root to the visible system-service error. This explains that dialog;
  it does not prove why client interiors are black. Do not run E itself as root.
- No system D-Bus socket/UPower causes cascading NULL-connection safety messages.
  The session D-Bus process is alive. These are separate buses, not failed SSH.
- DPMS is absent on Xvfb. Current main-log snapshot has1073 missing-extension
  messages and264 pairs of screensaver complaints. This is power-management
  polling noise from the headless X-server setup, not proof of GPU failure.
- INOTIFY_USER and SYSVIPC are disabled in the test kernel; the D-Bus inotify
  warning agrees with config. HIGHMEM is also disabled. UNIX98_PTYS is enabled.
- Animator timing messages show ~36–40ms waits against ~16.7ms expectations;
  they show missed timing, not a demonstrated crash or a specific QEMU bug.
- A current E eina_convert_dtoa warning reports a non-finite number; older
  wizard log also contains invalid Eo object IDs, and Terminology records a
  main-loop-lock mismatch plus one empty font-family safety failure. Preserve
  these for targeted reproduction; no established link to the arithmetic issue
  or black client interiors yet.
- Xvfb's log is empty. The sampled guest has about369MiB available; serial-log
  review finds no OOM kill, kernel oops, panic event or segfault (the kernel
  command-line panic option is not a panic). E, Xvfb and VNC remain running.

Next: use a matching minimal E profile and provision/disable optional service
integrations intentionally (issue7). Isolate direct client drawing from E's
non-SHM compositor readback (issue8), including a targeted finite-number probe.
These findings do not justify blaming all glitches on QEMU or advancing to
physical GPU acceptance.
