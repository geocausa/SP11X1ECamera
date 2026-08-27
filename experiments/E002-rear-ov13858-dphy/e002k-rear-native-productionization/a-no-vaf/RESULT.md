# E002k-A result — ACCEPTED

The E002h-r1 kernel and DTB were reused exactly. The only functional change was removing LDO16_B/VAF acquisition/voting from `ov13858`.

## Probe / identity

The patched module loaded with srcversion `4DB808B24637BDE41689BC5`. During probe only:

- LDO6_M / VIO 1.8 V;
- LDO1_M / VDIG 1.2 V;
- LDO5_M / VANA 2.8 V

were enabled. Native OV13858 identity and the accepted Surface mode-0 standby validation both passed. `vreg_l16b_camera_r3d enabled` event count remained **0**.

## Full transport

With defaults fixed and standard `test_pattern=1`, one 4076x2806 packed-GRBG10 frame dequeued normally (`bytesused=14321824`). SHA-256:

`6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346`

This is byte-for-byte identical to the accepted E002j color-bar frame captured when the old driver still voted LDO16_B. Thus removal of VAF has no effect on OV13858 pixel generation or transport.

After stream, test pattern was restored to Disabled, sensor runtime PM returned suspended/usage 0 and MCLK1/CSIPHY1/timer enable counts returned to zero. No LDO16_B enable vote occurred during either probe or stream.

**Conclusion:** LDO16_B 2.9 V is not an OV13858 sensor supply. Keep it outside the sensor driver for the future actuator/VAF device. The native sensor driver should own exactly VANA, VDIG and VIO.
