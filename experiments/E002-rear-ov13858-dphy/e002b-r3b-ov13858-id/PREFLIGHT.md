# E002b-r3b — rear OV13858 identity probe

Purpose: perform one controlled Windows-derived rear-camera D0/D3 power cycle and read the OV13858 chip ID. No CSI endpoint or streaming is enabled.

## Accepted base
- r3a camera-only RPMh provider: PASS.
- Command-db resources resolved with zero consumers/votes:
  - `ldom6` @ `0x00040d00` → 1.8 V
  - `ldom1` @ `0x00042000` → 1.2 V
  - `ldom5` @ `0x00041500` → 2.8 V
  - `ldob16` @ `0x00041400` → 2.9 V
- Golden Wi-Fi/audio were intact on r3a.

## r3b DT delta over r3a
- CCI0 master1 pinmux: GPIO103/GPIO104, `cci_i2c`.
- CCI0 master1 bus frequency: 400 kHz.
- rear client: CCI bus1 address `0x10`.
- reset: GPIO110 active-low.
- MCLK: CAM_CC_MCLK1_CLK.
- supplies: the four accepted custom r3b regulator phandles.
- No CSI endpoint and no stream path.
- Golden DT statements removed: **0**.

## Probe behavior
The existing vetted `sp11_ov13858_probe` performs:
1. set/cache LDO6_M 1.8 V, LDO1_M 1.2 V, LDO5_M 2.8 V, LDO16_B 2.9 V;
2. enable LDO6_M → LDO1_M → LDO5_M;
3. delay;
4. enable LDO16_B;
5. set/enable MCLK1 at 19.2 MHz;
6. release GPIO110 reset;
7. delay;
8. read register `0x300a` as three bytes, expected ID `0x00d855`;
9. assert reset, disable MCLK, disable rails in reverse order.

All failure paths unwind already-enabled resources. There is no streaming.

## Exact artifacts
- DTB SHA256: `a2cb276112532cf57766f74b8a884f8e921791e6fa0f61a469d95065888b8ab1`
- provider module SHA256: `ac9269cd4be0842cb5dd3eeef9ccc2dc95100c86b59e57d83b3d86c8f5178ace`
- probe module SHA256: `c945eb7e3f8aa4c142d4bf2f86c996fcd1b858764855d09518654b414de698be`
- candidate initrd SHA256: `bf8a08a33a37022c761ea7606a06920bdebf21fb1b5108d6a1c5a1dbc82a4eff`

The candidate initrd preserves the Golden uncompressed cpio prefix byte-for-byte and has exactly five semantic path deltas: one extra directory, two modules, one loader, and the ORDER override. The loader loads the sensor probe only if the camera RPMh provider has actually bound.

## Acceptance
Primary PASS: kernel log reports OV13858 ID `0x00d855` at `0x10`, followed by probe teardown.

Regardless of ID result:
- Wi-Fi and FullIO playback/capture must remain intact;
- custom camera regulators must return to disabled / zero users;
- MCLK1 must be disabled after probe;
- saved GRUB default must remain `sp11-audio-fullio-v19c`.
