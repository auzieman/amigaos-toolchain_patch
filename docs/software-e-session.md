# Software X11/E session build — 2026-10-31

The user requests a separate filesystem and a QEMU boot into basic E. Preserve
the current rescue image/guest while building this software-only test. The target
X server is Xvfb with x11vnc for a view into the guest's real X11 desktop; it
will not prove Radeon acceleration, physical HDMI or full SPE ABI correctness.
The unresolved directed-rounding issue remains GitHub issue3.

Current source dependencies are pinned in profiles/session-sources.lock.json.
Native tools image is
`sha256:d07f9edb80960f37cc40921171283aa7870151ae513d4789095d542e96f186d9`.
Native EFL generator packages are checked to source version1.28.1-1; host ELF
is x86_64. Target libraries remain separate, compiled from locked sources with
GCC8.5 SPE and the restored glibc sysroot. Independent source signature checking
is not claimed; DSC/archive hashes are checked. Public source/notice boundaries
remain component-specific.

Fresh source iterations retain their failures:

- 001 built Expat and FreeType, then Fontconfig requested automake-1.16.
- 002 attempted regeneration, revealing missing native autopoint.
- 003 uses upstream Fontconfig Meson successfully; JPEG, FriBidi and HarfBuzz
  also build. OpenSSL compiles but needs missing target `-latomic`.
- libatomic001 extracts the pinned GCC8.5 source archive afresh, builds only the
  matching target runtime, and passes threaded 64-bit add/CAS in the SPE guest.
  Preserve GPL3 plus GCC Runtime Library Exception3.1 notices.
- 004 carries forward completed library stages read-only, adds the separate
  atomic runtime and freshly builds OpenSSL/curl/D-Bus. Lua needs the generated
  Debian multiarch header; its package rules define the exact required content.
- 005 supplies that header for powerpc-linux-gnuspe and continues the remaining
  keyboard/font/server/VNC source builds. Status is recorded by its live receipt;
  no completion or graphical runtime result is claimed by this launch note.

Only installed outputs from completed preceding components are reused. Failed
components are extracted/repatched into fresh source directories; no partial
working source is silently resumed. Input file hashes, flags, commands, notices,
component state and target ELF output are retained by the runners. Base compiler,
sysroot and previous stages are mounted read-only. Native tool packages and font
data are not generic-PowerPC target binaries.

`build-efl-session.py` and profiles/images/efl-software-session.json prepare the
following cross EFL/E/Terminology slice. The runtime stager excludes build tools,
headers, static archives and documentation. Fonts and source notices are retained
as data. Existing shell/SSH/init stay available; a separate desktop-init prepares
the D-Bus machine ID then execs the existing PID1. Graphical startup stays an
explicit ordinary-user action via start-e-session. Both staging and startup
scripts need the actual target boot test before acceptance.

Evidence: docs/builds/r730-software-session-20261031. Missing atomic runtime is
tracked at https://github.com/auzieman/amigaos-toolchain_patch/issues/4.
