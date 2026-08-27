# E002k-B result — ACCEPTED

The production-style supply binding cleanup is behaviorally transparent on the physical SP11 rear camera.

## Accepted binding

The OV13858 node exposes only the standard sensor supplies:

- `dovdd-supply` -> the already-proven LDO6_M 1.8 V provider;
- `dvdd-supply` -> the already-proven LDO1_M 1.2 V provider;
- `avdd-supply` -> the already-proven LDO5_M 2.8 V provider.

The old board-local `ldo6m-supply`, `ldo1m-supply`, `ldo5m-supply` and `ldo16b-supply` properties are absent from the sensor node. VAF/LDO16_B remains external to the sensor.

## Runtime proof

Native identity and mode setup completed with the same physical rail order as E002k-A and **zero LDO16_B enable events**.

A single OV13858 Vertical Color Bar Type 1 frame captured successfully through the accepted native CAMSS route. It was exactly 14,321,824 bytes and SHA-256:

`6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346`

This is byte-for-byte identical to the accepted E002j and E002k-A deterministic sensor-generated frame.

After capture, `test_pattern` was restored to disabled, sensor runtime PM returned to suspended/usage 0, MCLK1/CSIPHY1/timer enable counts returned to zero, Wi-Fi/audio remained healthy, and no kernel fault was logged.

## Conclusion

**E002k-B ACCEPTED.** Standard Linux/OmniVision `dovdd`, `dvdd`, and `avdd` consumer names are proven equivalent to the earlier board-local names. LDO16_B/VAF does not belong in the OV13858 sensor power lifecycle.

Next: E002k-C removes the remaining `microsoft,e002*` experiment gates and selects the Surface mode from normal firmware/endpoint data rather than experiment-only properties.
