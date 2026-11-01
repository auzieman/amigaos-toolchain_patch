# Superseded archive experiment

These receipts retain the earlier mixed native/foreign archive and solver
experiment. Index signatures verified, but installing the patched SPE libc
beside stock amd64 libc hit Debian's exact-version coinstallation constraint.
The attempted amd64 libc rebuild was stopped at user direction and its build
route was removed. No native libc result is promoted.

The accepted next direction is powerpcspe-only package builds and target-only
archive/dependency resolution. See ../boot-candidate-20261101/README.md for the
new signed archive, dependency simulation, genuine header package and QEMU
kernel/storage evidence. Host utilities remain ordinary Debian binaries.
No configured root or completed disk image is established by these receipts.
