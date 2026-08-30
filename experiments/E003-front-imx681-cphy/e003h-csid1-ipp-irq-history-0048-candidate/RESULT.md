# E003h 0048 — CSID1 IPP IRQ-history result

The single authorized 0048 helper invocation was consumed on 2026-08-30. It returned `ETIMEDOUT` while waiting for VFE1 raw BUS Epoch0; no QC10C userspace output was produced. The wrapper archived evidence and immediately rebooted to the protected FullIO v19c Golden. There was no same-boot retry.

## Decisive observer result

The software-only in-ISR history recorded:

- OR history: `0x00e15ff8`
- last ISR-observed IPP value: `0x00004ee8`
- ISR samples: `4`

The OR history contains all five events that the old final timeout snapshot could not preserve: `CAMIF_EOF`, `CAMIF_SOF`, `CAMIF_EPOCH0`, `CAMIF_EPOCH1`, and `RUP_DONE`. Therefore the consumed 0042–0047 final `IPP_IRQ_STATUS=0x00011e00` snapshots remain valid instantaneous readings, but their historical inference that CSID CAMIF/RUP/Epoch never occurred is superseded.

The accepted same-machine Windows live IPP status is `0x00e11ff8`. Linux history is a strict superset by exactly `0x00004000`, bit14, mapped by the pinned CSID680 layout as `ERROR_LINE_COUNT`. This transient error was invisible in the final timeout status because the normal CSID ISR had already cleared it.

## Boundary after 0048

Sensor-to-CSID ingress is clean: 37,016 packets, zero ECC and zero CRC errors. CSID1 reaches CAMIF SOF/EOF, Epoch0/1 and RUP_DONE. RT-CDM reaches 17 FIFO BL completions with no fault. VFE1 still has `TOP_STATUS1=0x00030003`, `BUS_STATUS1=0`, exact Windows masks, exact FULL client state, and no raw BUS Epoch0 bit21.

The current failure boundary is therefore **after CSID1 CAMIF/RUP/Epoch progression and before VFE1 raw BUS Epoch0**. The transient CSID bit14 `ERROR_LINE_COUNT`, absent from the accepted Windows live status, is the strongest newly exposed mismatch and must be closed statically before any further Linux runtime.

Fail-closed extractor and analysis pin the raw run/post/dmesg/RT-CDM/Golden evidence byte-for-byte. Runtime is blocked again; do not repeat 0048.
