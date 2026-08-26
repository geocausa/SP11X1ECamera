# E002b-r3b result — SAFE FAIL at MCLK boundary

r3b successfully crossed the complete rear-camera regulator sequence using the accepted camera-only RPMh provider:

- LDO6_M → 1.8 V enabled
- LDO1_M → 1.2 V enabled
- LDO5_M → 2.8 V enabled
- LDO16_B → 2.9 V enabled

All four writes succeeded. The probe then returned `-EINVAL` before any chip-ID transfer log, and all four rails unwound cleanly in reverse order. Post-probe every custom regulator was `disabled` with `num_users=0`. Wi-Fi and both FullIO playback/capture remained functional.

The failure is after LDO16_B enable and before GPIO110 reset release / CCI chip-ID read. In the current probe this leaves two unlogged candidates:
- `clk_set_rate(MCLK1, 19200000)`
- `clk_prepare_enable(MCLK1)`

The explicit post-set rate mismatch branch did not log, so that branch was not observed.

## Windows static oracle confirmation
`CAMS_RES_MSHW0491.bin` SHA256 `2d356bbfaf07ced1e5c03014a5c496b12107f5dc489c4333052565d5a5a5dcc2` encodes the Windows D0 resource order:
LDO6_M → LDO1_M → LDO5_M → DELAY → LDO16_B → `cam_cc_mclk1_clk` → TLMMGPIO → DELAY.

Immediately following the `cam_cc_mclk1_clk` resource in the blob is little-endian `00 f8 24 01`, i.e. **19,200,000 Hz**. Therefore the Linux probe's requested 19.2 MHz matches Windows.

The X1E Linux CAMCC driver also lists 19.2 MHz as a native MCLK source rate (alongside 24 MHz and 68.571429 MHz), so the remaining failure is Linux clock plumbing/activation rather than a guessed Windows frequency.

No CSI endpoint or streaming was attempted.
