# Local AmigaOS SDK PCI reference inspection

Requested ~/Programs/SDK is absent; located ~/Projects/SDK instead.
Read-only inspection, no SDK code copied into Linux patches.

References:
- SDK/Documentation/AutoDocs/expansion.doc:1975, pci_device/SetEndian.
- SDK/include/include_h/expansion/pci.h:230, access endian enumeration.
- SDK/include/include_h/resources/radeoncp.h:83, register access helpers.

The PCI interface documents host-native conversion by default and an interface-local
access mode to change it. Documentation explicitly distinguishes software I/O access
conversion from changing device hardware endianness. This is I/O-interface guidance;
it must not be assumed to describe arbitrary mapped MMIO register access.

The Radeon resource header version 54.16 contains volatile 32-bit mapped register
loads/stores and PowerPC sync/eieio barriers. These helpers do not explicitly swap
the value. Mapping/device configuration context is not established, and this does
not prove the proprietary RadeonRX driver uses these helpers or this exact sequence.

Bounded search of Examples/include/Documentation found no Polaris SMU startup
implementation. These references support auditing both conversion and ordering,
not copying the helper or adding another swap/barrier without a Linux access audit.
Next compare Linux PowerPC writel/readl ordering and the SMU indirect index/data
transaction against these distinct access contracts, then validate upload readback.
