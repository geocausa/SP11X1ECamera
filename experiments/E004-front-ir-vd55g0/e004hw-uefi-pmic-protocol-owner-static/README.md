# E004hw — original UEFI PMIC interface owner of computed-register writer

**OFFLINE ORIGINAL FIRMWARE PASS, 2026-09-20.** The original PmicDxe image is SHA-pinned to
402315711a6761441234eac8c0cd3c0ad23cb4fdb7d0a9de3dd94c3ffac38dff. Original
PmicDxe+0x15394 constructs a two-interface firmware protocol registration, using
boot-services indirect method offset +0x148 (UEFI ABI InstallMultipleProtocolInterfaces).
The first GUID at +0x2f2b0 receives interface +0x2f4d0; the second GUID at
+0x2f190 receives interface +0x38b58, followed by a null terminator. Original
conditional initializer call sites are +0x19f0 and +0x1a58. This is a real
static registration ROUTE, not proof it completed in the running machine.

The second interface GUID is ae6ae96e-483f-42ae-9cc1-9fac1b584728.
The original E004hv function pointer +0x38d98 is therefore at second-interface
slot +0x240 (0x38d98 - 0x38b58), with ARM64 DIR64 relocation and original
target PmicDxe+0x222f8. It is an indirectly callable published PROTOCOL
METHOD CANDIDATE, not a demonstrated automatic boot initializer. An independent
original descriptor getter at +0x2003c (direct caller +0x1f3a8) returns
another structure pointer via +0x38b50 to +0x38b18; this is not the published
interface base.

The exact second-interface GUID appears in 13 of 255 archived UEFI PE images,
including the PmicDxe provider, QcomChargerDxeWp, DisplayDxe and BdsDxe.
This is a GUID-presence inventory, not proof that any consumer acquired the
protocol or called slot +0x240. The other registration GUID at +0x2f2b0
occurs only in the provider image.

The generic PMIC write helper obtains per-device metadata through +0x12a98,
whose +0x12b20..+0x12b28 indexes an original fourteen-entry descriptor-pointer
array at +0x39ef0. All 14 qwords are zero IN THE ARCHIVED PE FILE; this is
not a runtime memory measurement. The runtime base, periph stride, additional
offset, actual computed address, incoming w1 halfword and invocation remain
UNKNOWN. Relative offset 0x3e is NOT proof of absolute timer register 0xee3e.
The first timer byte 0x93 writer is still unidentified.

Verification: source pins the previous E004hv result, original firmware PE SHA,
original disassembly, registration GUIDs, table slot and relocation,
initializer/getter caller inventory, descriptor-slot on-disk contents and
the 255-image GUID inventory. 42 separate mutated in-memory original-image
negative tests fail closed. No OEM firmware bytes or raw face/camera data
are added to Git.

NEXT: trace original firmware protocol acquisition and a concrete slot +0x240
caller, if any, in GUID-containing images; then original w0/w1 provenance.
Independently seek reliable runtime descriptor base and stride authority.
An ordinary Windows KD session cannot by itself establish pre-OS execution,
so reserve the authorized one-shot Windows oracle boot for a discriminating
question. No firmware, kernel, DT, ESP, boot defaults, camera, PMIC, SPMI,
login or emitter hardware was modified. Protected Golden remains unchanged;
native IR illumination OFF and E004fs/E004ge independent physical emitter
cutoff gate remains BLOCKED.
