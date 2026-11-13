# Incremental QEMU and PNY installation goal

Build one genuine apt/dpkg-managed powerpcspe installation and validate the same
package manifest in QEMU and on the PNY. Keep platform-specific kernels/device
trees/boot scripts distinct and preserve physical rollback. Existing demo
shell/SSH/X/E remain reference evidence, not replacement Debian package records.

1. Index existing accepted target packages with receipt/hash checks and a signed
   repository. Resolve duplicate same-name/version outputs explicitly using the
   audited pool; never overwrite mismatched payloads silently.
2. Complete the pinned apt3.0.3 and target gpgv (gnupg2 2.4.7-21+deb13u1) closure.
   Sources are cached and registered in apt-ssh-sources-20261111.lock.json.
3. Build/configure the base normally: bash/coreutils/dpkg/apt, accounts, devices,
   mounts, networking and init. Configure packages/maintainer scripts; require
   clean dpkg audit and apt dependency checks in the booted guest.
4. Install/configure OpenSSH with normal permissions and per-install host keys.
   Verify remote login, shell commands, restart/reboot persistence and package
   installation from the signed repository. Do not copy server private keys.
5. Stage the matching accepted root on PNY and verify physical shell/network/SSH.
   Add packages incrementally to both through the same repository.
6. Install X11 terminal/input/fonts, then software Enlightenment. Require repaint,
   keyboard/mouse and overlapping-window tests; software rendering is deliberate.

Core follow-up: zlib manual012 clean build and payload verification passed.
Kerberos measured regcomp cache answer is registered; its manual013 request was
missing dependency inputs, so repeat through Debian's audited installation set.
libtirpc/libnsl follow Kerberos; Python/ALSA/audio follow their actual metadata.
Grep/GCC14 belongs to the separately qualified compiler follow-up, not a silent
compiler replacement during active jobs. Prepared incremental-workstation plan
includes apt, gnupg2, core libraries and the software workstation selection;
not submitted by this staging step.

Current PNY: serial0700993AAC40D602, verified file backup,1GiB FAT boot and
114.4GiB ext4 root, disk IDa1221111. Package root and physical boot acceptance
pending. Archive candidate002 is building; candidate001 stopped on conflicting
historical package payloads and was retained for diagnosis. No usable apt/SSH
installation is claimed until the above checks pass.
