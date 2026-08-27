# E002k-A preflight — remove VAF from OV13858-owned rails

Status: PREPARED / NOT YET BOOTED

## Single variable

Compared with accepted E002h-r1, remove LDO16_B 2.9 V from the OV13858 driver's regulator acquisition, voltage programming, power-on, power-off and error unwind paths.

Everything else stays fixed:

- exact Golden kernel;
- exact accepted E002h-r1 DTB, including CSIPHY1 8 KiB resource;
- exact RPMh provider;
- GPIO97 MCLK1 at 19.2 MHz;
- GPIO110 reset lifecycle;
- VIO/LDO6_M 1.8 V, VDIG/LDO1_M 1.2 V, VANA/LDO5_M 2.8 V;
- 4076x2806@30 Surface mode;
- LINK_FREQ 592.8 MHz;
- CSIPHY1 -> CSID0 -> VFE0 RDI0;
- normal V4L2 stream path.

The DT may still contain `ldo16b-supply`; the E002k-A driver deliberately does not request it. The provider may register LDO16_B but **must never log an enable vote** during probe or stream.

## Acceptance

1. native identity still passes;
2. no `vreg_l16b_camera_r3d enabled` event occurs;
3. standard test-pattern=1 produces one complete 4076x2806 packed-GRBG10 frame;
4. decoded frame retains the deterministic two-level 64/1023 vertical color-bar signature;
5. test pattern restored to 0;
6. three sensor rails, MCLK and CSIPHY tear down cleanly;
7. Wi-Fi/audio healthy and no kernel fault.

If accepted, production driver can use the standard three-supply OV sensor model and leave VAF to a future actuator device.
