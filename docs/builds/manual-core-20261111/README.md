# Direct core-library follow-through

Zlib manual012: standard clean sbuild completed exit0, six Debian binary outputs
verified by the package inspector (ELF32 big-endian PowerPC). Corrected bundled
minizip compiler/host selection and link-time rpath-link; no runtime RPATH added.
Receipt work/manual-zlib-20261111-012/receipt.json includes payload proof hash.
The broad scheduler was held while an existing worker slot became available and
released in a finally clause after completion; no SDK/cache/source deletion.

Kerberos configure's exact regcomp/regexec test was compiled using existing
GCC8.5 SPE SDK, executed with qemu-ppc -cpu e500v2, and printed
libc=2.41 result=0. Source/result/compile log retained here. Static probe checks
this libc predicate, not full Kerberos runtime. Added the measured cache answer
to the existing architecture-scoped packaging patch. Manual013 clean sbuild
is running with the same bounded slot/scheduler handling. Build/runtime
acceptance remains pending; no assumed pass for other blocked core libraries.

## Kerberos positional printf gate

Core014 passed regex but stopped on ac_cv_printf_positional. Exact positional
format probe (%2$x %1$d with100,512) compiled for SPE and ran under e500v2
QEMU: libc2.41, actual200 100, exit0. Source, compiler command, hashes and result
are retained as krb5-printf-* here. Added measured architecture-scoped
ac_cv_printf_positional=yes. Generated configure audit found only three explicit
fatal cross-run gates: constructor/destructor, regex and positional printf;
all have measured cache predicates now. Submitted core015 with the same
Debian-resolved nine-source dependency chain. Full package pass still pending.

## Core015 acceptance

Run015 completed: krb5,libtirpc,libnsl all produced Debian packages with successful
payload-inspected receipts. No compile failures in this run. Six consumers
remain dependency-blocked: audit needs libwrap0-dev; curl needs libnghttp2-dev;
PAM,OpenSSH,D-Bus,systemd await libaudit-dev. Package creation is accepted;
normal target installation and runtime are still separate gates.

## Broad prerequisite/workstation016

User requests widening beyond two immediate prerequisites. Authenticated pinned
intake cached13 producer sources: tcp-wrappers,nghttp2,nghttp3,ngtcp2,lm-sensors,
libassuan,libksba,npth,libusb-1.0,libpsl,libssh2,c-ares,publicsuffix. Added
source-lock/cache registrations and selected all195 sources including apt/GnuPG
and existing workstation closure. Submitted port-broad-core-20261111-016 via
standard dependency-ready pipeline,4 workers max. Existing accepted outputs
remain reusable. Historical failure import now covers all port-* run receipts,
not only obsolete port-pipeline-* names; fingerprints still control retries.
This is source/cache intake and submission, not195 package completion.
