# E004ax — Surface SecureISP logical IFE core selection

## Result

**PASS: the exact SP11 SecureISP trustlet allocates a one-entry active-core list containing logical IFE core 3, and both secure IFE and secure CSID initialization consume that same list.**

Combined with E004aw, core 3 selects the **IFE-Lite** HAL family.

No Linux SecureISP runtime occurred.

## One active logical core

On the first DeviceConfig resource-allocation path, the trustlet writes:

- active core list entry 0 = `3`;
- active core count = `1`.

It then immediately calls the secure IFE open routine using the list entry. The subsequent secure CSID initialization loop reads the same list and count.

The same list is reused by later start, stop, packet-send, set-info and resource-management loops. This is not an isolated diagnostic constant.

## Independent Windows KMD corroboration

The same-machine CameraSecureISP kernel driver contains the clock-vote diagnostic:

`ife3 clock request`

in the path that parses and applies the SecureISP packet's IFE clock configuration.

That is independent host-side corroboration for the trustlet's one-entry core-3 selection.

## E004aw cross-check

E004aw proved that the trustlet maps logical core IDs as:

- cores 0/1 -> full IFE HAL;
- cores 2/3 -> IFE-Lite HAL.

Therefore the exact SecureISP binary's active logical core 3 uses the **IFE-Lite** callback table and the lite secure-base topology:

- secure CSID view: base + `0x0000`;
- secure bus-writer view: base + `0x1200`.

The IFE-Lite hardware-version getter is installed for this core and is sampled after power-on.

## Scope

E004ax establishes the logical secure worker core selected by the exact installed SP11 SecureISP binary. It does not claim that Linux's ordinary CAMSS core numbering has the same namespace, and it does not equate this secure logical core with a non-secure MMIO block.

That distinction remains important because E004y proved that protected Windows IR frames flow while the ordinary observable CSID/VFE path stays inactive.

## Evidence

- `evidence/TRUSTLET-CORE3-LIFECYCLE.txt`
- `evidence/KMD-IFE3-CLOCK.txt`
- `evidence/CORE3-TO-LITE.txt`

## Safety boundary

No qcomtee module was loaded. No secure aperture was mapped from Linux. No camera-domain memory ownership changed. No secure CSI SIP call or SecureISP task was issued.

SP11 remains on protected Golden Linux.

## Next static gate

Map the core-3 IFE-Lite callback/register family against the Linux Qualcomm camera sources and X1E hardware descriptions. The goal is to separate reusable register semantics from operations that must remain inside a protected execution context; do not access the protected aperture from Linux.
