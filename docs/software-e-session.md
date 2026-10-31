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

## Target server proof and EFL build

All software-session dependency packages now compile. Corrected old CMake install
path handling by using absolute `/usr/lib`, rebuilding JPEG/VNC, and dropping
only the erroneous build-work subtree in the new copied stage. Set the X server's
font path explicitly to the actual image's core-font directory plus built-ins;
fontutil was used only to infer a default path, not to provide runtime code.
Minimal libsndfile is required by E's unconditional Ecore Audio API dependency;
PulseAudio/device backends remain disabled. EFL also unconditionally requires
GIF support despite its loader-disable option, so the locked giflib is included.

EFL1.28.1 builds in fresh efl-session004 (1,892 steps). Native generators stay
x86_64; staged runtime ELF files are PPC32 big-endian. An intermediate root
x11-root001 boots separately as software-x11001, 2GiB / 2 virtual e500v2 CPUs.
Shell and key-only SSH work, OpenSSL executes, and Fontconfig discovers DejaVu
and core X fonts. Actual target Xvfb and x11vnc run inside that guest. The minimal
kernel's XShm path is disabled, so VNC uses `-noshm`; prepare root-owned1777
/tmp/.X11-unix before ordinary-user server startup in the next image.

The reused original probe banner referred to a native server; a fresh generic
banner and runner-scoped server identity remove that ambiguity. The new proof
explicitly records **SPE Xvfb inside software-x11001**. Pixel readback,
Render/RandR/XFixes and XCB request/reply pass with both ends inside SPE QEMU.
RFB3.8 responds through the loopback-only SSH forward. This is still not E,
physical Radeon/HDMI, GL or complete arithmetic acceptance.

E-session001 stops at an unconditional required Eeze probe despite both relevant
options being false. E-session002 passes configuration after guarding that probe,
then exposes unguarded ACPI watcher types in the privileged hardware helper.
The ordered e17 patch series makes the probe optional and skips Eeze-dependent
ACPI watchers when HAVE_EEZE is absent. Explicit integration requirements remain
in their existing later checks; Eeze-present functionality is unchanged by the
source guards. Fresh e-session003 rebuilds the selected minimal E configuration.
Issue6 tracks this; full Eeze-enabled runtime is not tested by this software lane.


## E build and filesystem boot

E-session003 exposed one more no-Eeze wizard guard: keep the NULL temperature
list declared so the existing filesystem fallback can run. The three ordered,
hash-checked local patches apply after Debian's supplied e17 patches. E builds
in e-session004; Terminology then rejects an unsupported docs option. Removing
that option gives a completed e-session005 with PPC32 big-endian runtime ELF.
Full Eeze-enabled behavior remains untested.

Root assembly001 failed on a duplicate identical MIME definition. A chained
launch incorrectly continued with its incomplete archive; that test guest was
stopped. The stager now deduplicates identical overlay inputs and rejects
conflicting data. The launcher checks a completed receipt and archive hash
before making a launch directory. A negative test rejects the incomplete001
archive without creating a launch directory.

The stock E wallpaper gallery accounted for over400MiB and is excluded; the
user's four theme EDJs and selected still wallpapers remain private lab inputs.
No theme binaries or commercial media are committed. The revised root002 is
307,780,160 bytes raw, 187,496,749 bytes deterministic gzip; decompression hash
matches the raw receipt. This QEMU kernel has RD_GZIP but no HIGHMEM: although
2GiB is configured, MemTotal is771,760KiB. Software-e002 filled the default tmpfs
root limit; software-e003 selects rootfstype=ramfs and boots cleanly with shell,
key-only SSH, machine-ID initialization, target Xvfb and x11vnc. Over400MiB was
available before desktop startup. These are software-test boot arguments, not
physical A1222/U-Boot instructions.

E0.27.1 renders its first-run wizard through the target Xvfb/VNC server, accepts
pointer input and advances through the standard computer profile. Initial
language/keyboard lists are empty in this stripped image; defaults can advance.
Locale/keyboard selection completeness, missing system-bus/UPower and kernel
inotify support remain follow-ups, not silently accepted hardware integration.
The dedicated desktop4 browser now uses loopback noVNC6089 forwarding to this
separate guest. Existing rescue guest remains running.

The standard profile completes and shows the desktop shelf/icons, but client
interiors remain black, including Terminology and E warning dialogs. This is a
partial graphical boot with an unresolved rendering failure (issue8), not a
usable clean-desktop pass. Issue7 tracks locale/keyboard and optional integration
work. The screenshot and graphical-result.json preserve this distinction. Next
isolate non-SHM redirected-pixmap readback from direct client drawing; do not
assume an SPE arithmetic cause. Physical boot and GPU tests remain separate.
