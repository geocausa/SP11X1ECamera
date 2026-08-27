# E002g — Windows 207-register oracle equivalence

The exact installed Microsoft/Qualcomm rear sensor package is used **locally only** as a clean-room oracle. The proprietary 207-entry table is not committed or redistributed.

## Offline comparison

The exact mode-0 `regSetting` block contains 207 writes to 207 unique addresses. Its final register map was compared mechanically with the E002f native reconstruction:

1. 12-register clean-room Surface 592.8 MHz PLL;
2. unchanged GPL upstream `mode_4224x3136_regs` common table;
3. 24-register clean-room Surface mode-0 override list;
4. normal final VTS control write to 3214.

Results:

- Windows mode-0 unique registers: **207**;
- Windows registers absent from the clean reconstruction: **0**;
- differing Windows-covered register values after final VTS: **0**;
- one Linux-only register remains: `0x4503 = 0x00`, the upstream explicit test-pattern-disabled state.

Before the final VTS control write, the only Windows-covered state difference is exactly the expected static-table VTS (`0x0c88`) versus runtime/QTI VTS (`0x0c8e`).

## Engineering consequence

There is no technical benefit to embedding the proprietary 207-entry table into the public/native driver. The clean reconstruction reaches the same Windows-covered final sensor state while preserving provenance:

- common values remain sourced from upstream Linux;
- Surface-specific facts remain a compact clean-room delta;
- the Windows table remains a local validation oracle.

This is the preferred implementation path unless later streaming evidence proves write-order sensitivity that the standby validation did not reveal.
