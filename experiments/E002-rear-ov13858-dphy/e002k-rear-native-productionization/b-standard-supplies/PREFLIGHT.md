# E002k-B preflight — standard OV13858 supply bindings

Status: PREPARED / NOT YET BOOTED

## Single semantic variable

E002k-B preserves accepted E002k-A sensor power behaviour while replacing experiment/board consumer names with standard Linux OmniVision supply names:

- `dovdd` -> proven LDO6_M / VIO / 1.8 V;
- `dvdd` -> proven LDO1_M / VDIG / 1.2 V;
- `avdd` -> proven LDO5_M / VANA / 2.8 V.

LDO16_B/VAF is absent from the sensor node and driver, as accepted in E002k-A.

Power enable order remains `dovdd -> dvdd -> avdd -> delay -> MCLK -> reset release`; disable order remains reset -> MCLK -> avdd -> dvdd -> dovdd.

## DT mechanical proof

Starting from the exact accepted E002h-r1 DTB, the sensor node changes only:

Removed:
- `ldo6m-supply`
- `ldo1m-supply`
- `ldo5m-supply`
- `ldo16b-supply`

Added:
- `dovdd-supply` with the exact old LDO6_M phandle;
- `dvdd-supply` with the exact old LDO1_M phandle;
- `avdd-supply` with the exact old LDO5_M phandle.

All other sensor-node properties and values are identical. Global decompile shows only those seven property lines changed. Existing DTC warnings are byte-identical 30 -> 30.

## Everything else fixed

- Golden kernel unchanged;
- RPMh provider unchanged;
- GPIO97/MCLK1 19.2 MHz unchanged;
- GPIO110 reset unchanged;
- E002h-r1 CSIPHY1 8 KiB resource unchanged;
- 4076x2806@30 mode and all Surface register deltas unchanged;
- LINK_FREQ 592.8 MHz and VT pixel rate 432732960 Hz unchanged;
- graph/routing unchanged;
- experiment stream/mode properties remain for this naming-only gate.

## Acceptance

1. patched module binds and native identity passes;
2. dmesg shows the same physical three rail enable/disable sequence;
3. no LDO16_B enable event;
4. standard test-pattern=1 produces exactly one complete 14,321,824-byte frame;
5. raw SHA-256 equals accepted deterministic pattern `6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346`;
6. test pattern restored to zero;
7. runtime PM/clock teardown and Wi-Fi/audio remain healthy.
