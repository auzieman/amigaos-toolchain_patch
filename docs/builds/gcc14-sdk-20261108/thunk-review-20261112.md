# GCC14 C++ qualification resume — 2026-11-12

R730 reachable after reboot. Retained GCC14 qualification002 failed linking
libstdc++; no new package batch or GCC8 compilation launched.

Exact undefined symbols:
- _ZThn8_NSt9strstreamD1Ev
- _ZTv0_n12_NSt9strstreamD1Ev

The corresponding D0 thunks are defined. Both undefined D1 thunk references
already occur in strstream.o, so this is earlier than shared-library packaging.
Recompiled the exact strstream.cc invocation from retained build.log using the
existing GCC14 compiler, source and sysroot mounted read-only, 1CPU/2GiB,
network disabled, emitting assembly only into a new evidence directory.

Evidence: work/gcc14-thunk-review-20261112-001 on R730. Four successful compiler
invocations: baseline O2, -fno-ipa-icf, -O0, and devirtualization disabled. All
contain the missing thunks' code sections and vtable references but neither
callable symbol label. Thus neither changing ICF nor these optimization settings
repairs the missing definitions. No compiler source patch or runtime rebuild yet.
Next: compare actual compiler thunk-emission implementation/build provenance
with rs6000-call.cc and generic assemble_start_function, then reproduce with a
minimal multiple/virtual-inheritance destructor case before a bounded rebuild.
Full SDK/package rebuild remains gated on compiler/runtime qualification.
