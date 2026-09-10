# DA static proof

- W: `request_frame = source_generation + 3`, 104/104 ordinary front matches.
- CX: Windows sensor packet F selected at KMD SOF coordinate F-1; register list synchronously reaches I2C submit.
- CY: one atomic write after DQBUF sequence0 / generation1; G2 baseline-like; G3 first strong BHist drop; one hardware step transaction; Golden return PASS.
- CP start exposure: 33,333,332 in Short/Long/Safe/S1.
- CH/CQ cold bootstrap: gain1/time33333332 -> FLL3562/VBLANK1402/exposure3554/again0/dgain0x0100/ISP1.

Linux delayed schedule:

`stats G -> compute tuple -> wait through completion G+1 -> write -> measured sensor boundary +2 from write-source completion -> first effect G+3`.

This is a Linux scheduling contract aligned to Windows request identity. No additional Windows optical-frame assertion is introduced.
