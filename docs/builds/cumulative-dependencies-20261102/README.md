# Cumulative Debian cross-build dependency closure — 2026-11-02

The prior core510 pass completed with16 source groups built,52 blocked by
Debian build dependencies and2 real compile failures. Its fixed build-root
image meant successful library/development outputs never unlocked subsequent
sources. `prior-core510-queue.json` retains that complete result; builds are
not target package installation or boot acceptance.

## Workflow correction

The serial queue now optionally accumulates receipt/hash-pinned SPE
Multi-Arch:same library/development packages into new immutable cross-build
images through normal apt/dpkg. It statically inspects package ELF payloads,
checks dependency/version/shared-file rules, prohibits removals, isolates the
installation from the network and checks that native package state is unchanged.
Failures preserve the prior accepted image and remain deferred. Target tools,
services and architecture-independent data are not automatically installed into
the native build root; their final target installation is a separate stage.

Blocked sources are retried after the installed dependency environment changes.
A compile failure is retained for a reviewed source/recipe fix, rather than
repeated indefinitely. The queue keeps attempt history, latest source states,
current image digest and required full rebuilds. Library installs that initially
lack dependencies receive another opportunity after the pass. This is a
bootstrap cross-build-root workflow; it does not claim to be a complete apt
archive dependency scheduler or a configured target OS.

Two focused scheduler tests verify that a later prerequisite unlocks an earlier
consumer, compile failures do not spin, and failed dependency installation
preserves the parent image. Real library installation/retry acceptance follows
in the constrained R730 queue. No laptop compilation or new viewer is started.

## Consumer fixes

* grep3.11-4: Debian's stray-backslash warning patch places a declaration
  immediately after a label. A null statement preserves behavior and allows
  the pinned GCC8 compiler. Version/hash-pinned source patch applies cleanly.
* Managed builds stop exporting absolute CC/CXX. Debian selects standard
  tuple-prefixed installed tools using its cross architecture and PATH. This
  avoids OpenSSL prepending CROSS_COMPILE to an absolute CC path. Installed
  compiler default ABI/sysroot checks remain mandatory.

Issues19/20/21 track cumulative readiness, grep and OpenSSL respectively.
Full compilation, target execution and physical validation remain distinct.

## New prerequisite intake

Authenticated Debian trixie/security Release/Sources records pin libbsd0.12.2-2,
readline8.2-6, libffi3.4.8-2 and brotli1.1.0-2+deb13u1. The source lock records
all file hashes; separate DSC signer verification is not claimed. Existing
configured Debian Signed-By trust is reused, including security sources rather
than silently dropping their updates. Raw copyright files are retained here.

License review: libbsd has BSD/ISC/Expat and documented per-file variants;
readline is GPL3-family with documentation/auxiliary-file exceptions; libffi
has Expat/X11 plus documented auxiliary/test/script terms; Brotli is MIT.
Keep upstream per-file notices and Debian copyright files in packages; no
relicensing or vendor/Hyperion code import occurs. This intake covers generic
Linux dependencies, not an AmigaOS runtime.

Native build helpers are installed from existing Debian binaries via
Dockerfile.native-closure-tools; native source compilation is not expanded.
The native helper image is
sha256:2a7ec2a794837b994c84a3a8f4cd01d63041845407e3fa284c9c57786d5c8e70;
installed managed compiler checks pass. Target packages still compile only
for powerpcspe.

## Bootstrap and remaining gates

The libselinux queue entry explicitly uses supported nopython/noruby profiles
to bootstrap its core C library. It does not provide Python/Ruby bindings;
the required full rebuild remains in the queue receipt. Complete target
Essential/desktop closure and configuration, the normal-feature libc stage,
new QEMU graphical acceptance and real A1222 boot remain pending.

First cumulative001 installation rejected apt --no-download with local package
paths (internal relative pathname error). The parent image was correctly kept.
Remove that option: Docker network=none still prevents downloads, while normal
local apt installation remains intact. Preserve this failed attempt and use a
fresh frozen submission for the correction; do not edit a running snapshot.

## Real install and build checkpoints

Corrected cumulative002 installs libxcvt, libselinux's C development/runtime
pair, libbsd and readline through apt with clean audit and unchanged native
package state. Accepted current image:
sha256:61707ac68ec84d325f1c608662678821b8a6dd9415b5308ffbf1456d7148f7a6.
Grep520 builds with its source patch; static inspection validates its ELF32
big-endian PowerPC executable. Libselinux520 (explicit library bootstrap),
libbsd540, readline540, findutils540 and sed540 finish packaging. Findutils/sed
previously failed readiness on SELinux and now build against the installed
library: real dependency feedback, not just a mocked scheduler test.

Cumulative002 also exposes an infrastructure guard issue: its legacy tabor-*
container-name guard treats a lightweight metadata reader as a competing
compile, causing51 latest entries to be marked attempt-failed. Those are not
package compile failures. Preserve the interrupted/skipped history; the revised
guard permits only explicitly labelled metadata readers and waits for actual
build slots. A regression test covers metadata coexistence. Subsequent fresh
iterations reuse these successful outputs and reattempt the skipped sources.

OpenSSL540 gets past the invalid CC path and exposes an unconditional Debian
-fzero-call-used-regs=used-gpr flag unsupported by GCC8. A separate pinned
Configure patch compile-tests that mitigation with the resolved target compiler,
retains it when supported and explicitly warns otherwise. Losing this mitigation
on GCC8 is a documented bootstrap limitation. Source application is checked;
full patched OpenSSL packaging remains pending. No other hardening defaults
or runtime features are removed.

Native prerequisite expansion now uses Debian apt-get build-dep for the pinned
reviewed source scope, installing existing native binaries (not rebuilding
amd64). It preserves per-source failures and clean dpkg audit. Target package
readiness still requires genuine SPE libraries, not these native counterparts.
The source-closure planner maps real unmet library/development relationships to
authenticated source metadata and lists native/ambiguous roles separately. Its
output is candidate intake, not build readiness or an authoritative order.
