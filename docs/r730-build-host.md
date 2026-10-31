# R730 build and emulation host

The reinstalled `r730-trixie` at `10.20.0.130` is the larger build workspace.
Its Dell identity and root filesystem UUID match the retained October 5
installation receipt. Access routes through lab edge; the old global SSH host
entry remains untouched. A separate operator host-key record tracks this install.

Host preparation uses `scripts/prepare-debian-build-host.sh owner
/srv/data1/tabor-build`. It installs Debian 13 host tools, QEMU x86/PowerPC,
libvirt and Docker. It adds the operator to kvm/libvirt, with Docker remaining
root-managed. Sources and target toolchain versions remain independently pinned
by the existing build recipes; a distro host package install is not an exact
reproducible build environment.

The workspace uses an existing mounted data filesystem. Never repartition or
reuse the resale installer to prepare it. Keep cached archives, fresh per-run
source/object directories and retained results separate. Start substantial
builds at four CPUs and 8 GiB; existing two-CPU/4-GiB recipes also remain valid.
Target images retain the ultra-minimal package policy regardless of host tools.

`scripts/kvm-host-smoke.py` runs a temporary diskless x86 ROM. It checks QMP
`query-kvm`, executes guest instructions and checks CPUID VMX visibility. This
does not boot a nested hypervisor or an L2 guest. The accepted PowerPC shell
smoke test separately uses TCG: x86 VT-x does not accelerate PowerPC code.

The RTX 3060 Ti (`10de:2486`) and its audio function (`10de:228b`) occupy IOMMU
group 28 together. This is a passthrough candidate, not a completed assignment.
Its host driver remains attached. No GPU reset, guest driver or PowerPC guest
compatibility is inferred from IOMMU discovery. Host display, PCI binding, BIOS
and boot configuration are not changed by this preparation.

The mandatory first-login password change was completed. Current credentials
remain in a mode-0600 operator note outside this repository; no passwords,
private keys or media belong in commits. The existing BKC public key is installed
for the ordinary owner account; sudo still requires authentication.

References: [QEMU acceleration options](https://www.qemu.org/docs/master/system/invocation.html),
[kernel nested KVM guidance](https://docs.kernel.org/virt/kvm/x86/running-nested-guests.html).
