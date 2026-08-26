# E002b preflight — rear OV13858 probe only

Goal: prove the physical rear sensor identity without enabling CSI transport or registering a camera sensor with V4L2.

## Windows-derived route and D0 order

- CCI0 master1, 400 kHz FAST control bus
- Linux 7-bit address `0x10`
- reset GPIO110, active-low
- PM8010 `LDO6_M` = 1.8 V
- PM8010 `LDO1_M` = 1.2 V
- PM8010 `LDO5_M` = 2.8 V
- PM8550 `LDO16_B` = 2.9 V
- MCLK1 = 19.2 MHz
- ID bytes read from `0x300a..0x300c`, expected `0x00d855`

The Windows AeoB ordering is preserved. The probe shim deliberately uses conservative 1 ms / 10 ms waits at the two Windows delay points; E002b is an identity/safety gate, not final delay parity.

## Linux rail mapping

Windows suffix `M` is mechanically identified as the X1E PM8010 RPMh namespace (`qcom,pmic-id = "m"`). E002b adds only PM8010 LDO1/LDO5/LDO6. The X1E parent-supply topology is:

- LDO1/2 <- `vreg_s5j_1p2`
- LDO5 <- `vreg_bob1`
- LDO6 <- `vreg_s4c_1p8`

Windows `LDO16_B` maps directly to PM8550 RPMh ID `b`, LDO16; the existing Golden regulator group already provides its BOB1 input-supply relationship.

## Probe module

`sp11_ov13858_probe.c` is intentionally not a V4L2 driver. On one matching DT client it:

1. acquires GPIO110 asserted;
2. enables LDO6_M -> LDO1_M -> LDO5_M;
3. waits conservatively;
4. enables LDO16_B;
5. sets/enables MCLK1 at 19.2 MHz;
6. releases reset;
7. reads 3-byte ID at `0x300a`;
8. logs PASS only for `0x00d855`;
9. immediately asserts reset, disables MCLK and disables all four rails in reverse order.

No endpoint exists, so it cannot stream.

External-module vermagic is exactly `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`.

## Candidate hashes

- module: `c945eb7e3f8aa4c142d4bf2f86c996fcd1b858764855d09518654b414de698be`
- overlay DTBO: `7e3fa091856916469b418773232618d6a0ed6f2369421725f201a133587ab5f3`
- merged E002b DTB: `c83de02e88442ca7044ced81e145109b710074cb3b30e2a0109455a54f5a9d35`

The sorted base-to-candidate DT diff has no removed Golden lines.
