# Kerberos cross-configure qualification

Round018 finished with seven accepted source builds /15 inspected debs:
Xft, Xext, Xss, Xpm, Xaw, libdaemon and x11-xkb-utils. The existing Python,
BLT and Xxf86vm corrections are in active round020. Kerberos now reaches
configure and fails its constructor/destructor runtime test while crossing.
This blocks RPC/NIS/Python and the audit/SSH closure; it is not an SPE opcode
failure or an archive-download problem.

Debian dpkg-cross2.6.20 already carries the same Kerberos cache predicate:
https://sources.debian.org/src/dpkg-cross/2.6.20/config/cross-config.cache/
Debian cross-building documentation describes configure site cache use:
https://wiki.debian.org/CrossCompiling

Measured constructor/destructor startup/exit behavior separately with the
actual pinned GCC8/tabor6 and receipt-hash-verified glibc2.41 libc6/libc6-dev
packages. Static and dynamic SPE executables pass in qemu-ppc -cpu e500v2.
The dynamic probe sysroot uses the standard merged-/usr lib symlink; this
isolated extracted test fixture is not an assembled/accepted Debian image.
The first dynamic link attempt lacked that layout and failed before execution;
no target runtime success was claimed for it. The initial unprivileged probe
could not create a server-owned work directory; bounded root service ran it.

The source patch exports only this independently measured cache predicate in
Debian rules, restricted to powerpcspe cross builds using standard dpkg
architecture variables. It changes no native/other-target build and adds no
foreign-code execution to the package-build process. Normal package outputs,
maintainer scripts, dependencies and pinned source version remain unchanged.
Do not import the entire stock PowerPC site file: SPE ABI-specific values need
independent review, and existing Xorg probe semantics remain authoritative.

Actual patched source application/repack passed. Full Kerberos build, shared
library unload semantics, desktop acceptance and physical hardware remain
unvalidated. run-probe.py records the bounded R730 qualification recipe;
execute there under a1-CPU/1GiB service, never on the laptop. Source and compiler
hashes and exact commands are retained in receipts. This is a separate runtime
validation step, not a build-dependency generator.

Source preparation001 rejected a copied specification pointing at the wrong source lock before patch application; corrected to the existing signed port-dependency lock/cache. Source preparation002 passed. No failed proof was submitted as a build. Copy bench/constructor-destructor-check.c to /tmp/constructor-destructor-check.c on R730 before running the retained probe recipe; select a fresh output directory for a repeat.
