# AmigaOS SSH server preflight — 2026-11-05

A1222 / AmigaOS4 SSH preflight — 2026-11-05

STATUS: public-key and read-only diagnostic bundle. NOT a working SSH server installer.
Extract into a new directory. From AmigaShell, CD there and run:
  Execute Collect-SSH-Info
Read RAM:a1222-ssh-info.txt before uploading it to the lab FTP uploads folder.
The report checks versions and system status; it does not read passwords or keys.
Missing commands/files are expected diagnostic output. Do not post the report publicly.

operator.pub is the dedicated operator Ed25519 PUBLIC key only.
Fingerprint: SHA256:fO7nBfUWiBEuioKK14YQOLlY7UqkeNXHMlCt/WRcsuM
Keep the corresponding private key on the operator laptop. Never transfer it here.
Do not install operator.pub into a guessed path: the selected server determines
its authorized-key location and user/account model. Device host private keys
must be generated on the Amiga and retained there. Verify their fingerprint
before the first connection. Do not disable host-key checking.

Server qualification findings:
* OS4Depot OpenSSH 53.6 (2010, OpenSSH 5.5p1) lists client tools, not sshd.
  https://www.os4depot.net/?function=showfile&file=network/misc/openssh.lha
* Aminet BebboSSH 1.45 includes bebbosshd and Ed25519, but is m68k-amigaos.
  https://aminet.net/package/comm/net/bebbossh
  Archive SHA256 b959b8431dd608b46a5f93ab59957bff238940d14667572143dfe47206df7e7c
* Inspected author source 4c0b77279b5cd1cbe792964a42748f299051469e:
  https://franke.ms/git/bebbo/bebbossh
  src/rand.c and src/log.c use classic custom-chip address 0xdff000 under
  __AMIGA__. That needs review for OS4/A1222; a crash cause is not yet proven.
  This source revision is newer than the downloaded binary release.
* A loopback-only test of the release Linux reference daemon accepted a TCP
  connection but timed out before command completion. Key login is NOT verified.
  The temporary server and tunnel were stopped.

No server binary, default passwords, private keys, startup changes, or global
LIBS/ENVARC replacements are included. We need a qualified native OS4 server
or a reviewed port before supplying a proper key-only sshd installer.
LAN-only access remains the scope. The Linux USB rescue sshd is a separate ABI.

Published LAN FTP artifact: `downloads/a1222-os4-ssh-preflight-20261105.zip`

ZIP SHA256: `54f9f13497e3a19ecef390049117d908003e420125150cf5baaa804bcf693c36`. ZIP integrity, exact four-member allowlist and absence of private-key markers verified before upload. Only the dedicated public key was read; the operator private key remains local. No Amiga server/login acceptance is claimed.
