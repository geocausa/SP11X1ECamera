# E004az — Linux CSID680 vs SecureISP CSID-Lite parity

## Result

**PASS: the SecureISP trustlet's CSID-Lite function table matches the register layout already implemented by Linux `camss-csid-680` for X1E.**

This is a static parity result. It does not yet prove that the exact Surface DeviceConfig selector chooses the CSID-Lite table at runtime.

No Linux SecureISP runtime occurred.

## X1E Linux resource model

Linux 7.1.5 exposes five X1E CSID resources:

- CSID0, CSID1, CSID2
- CSID_LITE0, CSID_LITE1

All use `csid_ops_680`; the two lite resources are explicitly marked `is_lite = true`.

## Trustlet CSID-Lite match

The trustlet's alternate CSID table identifies itself through its diagnostics as `CSID_Lite`. Its register accesses align with Linux `camss-csid-680.c` across the full control path, not just one or two offsets.

Exact matches include:

- top IRQ status/clear: `0x7c / 0x84`
- buffer-done IRQ status/clear: `0x8c / 0x94`
- CSI2 RX IRQ status/clear: `0x9c / 0xa4`
- per-RDI IRQ status: `0xec + 0x10*n`
- per-RDI IRQ clear: `0xf4 + 0x10*n`
- CSI2 RX configuration: `0x200 / 0x204`
- RDI configuration/control: `0x500 / 0x504 / 0x510 + 0x100*n`
- epoch and frame/pixel/line-drop windows at `0x52c`, `0x540..0x564 + 0x100*n`

The trustlet also uses the same four-RDI status spacing for its CSID-Lite helper: RDI0/1/2/3 status at `0xec/0xfc/0x10c/0x11c`.

## Scope of the claim

The trustlet contains two distinct CSID HAL tables. E004az establishes that the table explicitly reporting itself as **CSID_Lite** is the same 680-generation register family Linux already models.

E004az deliberately does **not** claim that the Surface IR DeviceConfig selector bit chooses this table. The selector is copied into manager state at `+0xe00`, but its exact semantic ownership and exact SP11 value remain the next static gate.

The full/alternate table is retained as a separate implementation and is not collapsed into the lite table.

## Architectural consequence

Combined with E004ay, upstream Linux already knows the register semantics for both major non-transport pieces of the protected worker:

1. X1E IFE-Lite / VFE680 bus and DMA geometry;
2. X1E CSID680/CSID-Lite receive and RDI geometry.

What remains missing is the protected ownership/transport and exact secure lifecycle, not a wholesale rediscovery of the X1E camera register model.

This does not make direct non-secure access to the protected aperture valid.

## Evidence

- `evidence/TRUSTLET-CSID-LITE.txt`
- `evidence/LINUX-CSID680.txt`
- `evidence/LINUX-X1E-CSID-RESOURCES.txt`
- `evidence/PARITY-MAP.txt`
- `ghidra/TRUSTLET-CSID-HAL.txt`
- `ghidra/TRUSTLET-CSID-IRQ-HELPERS.txt`

## Safety boundary

No QCOMTEE module was loaded. No protected aperture was mapped. No CP_CAMERA ownership changed. No secure CSI SIP call or SecureISP task was sent from Linux.

SP11 remains on protected Golden Linux.

## Next static gate

Resolve the DeviceConfig selector copied to manager `+0xe00`, prove its semantic meaning, and determine which CSID HAL table the exact Surface IR configuration selects.
