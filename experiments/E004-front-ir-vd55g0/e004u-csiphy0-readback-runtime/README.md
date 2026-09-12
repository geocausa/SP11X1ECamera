# E004u — one-shot CSIPHY0 Windows 96/96 receiver readback

E004u is the first runtime stage that is allowed to program the Linux CSIPHY0 receiver for front IR.

It deliberately does **not** stream the VD55G0 sensor and does not configure CSID/VFE or illumination.

The candidate combines unchanged, already-proven artifacts:

- E004o IR-only graph DT;
- E004l native VD55G0 sensor module;
- E004k scoped CAMSS receiver-parity module with `e004j_ir_dphy_windows_parity=1`;
- E004t receiver-only readback harness.

Runtime sequence:

1. dynamically identify the physical VD55G0 by OF compatible + address 0x60;
2. load CAMSS and native sensor;
3. wait for native sensor initialization, graph completion and runtime suspend;
4. require the immutable sensor -> msm_csiphy0 link;
5. insert the E004t harness;
6. E004t requires the sensor still suspended and no enabled CSIPHY0 -> CSID link;
7. E004t powers CSIPHY0 only, programs it through its normal `.s_stream(1)` callback, and reads the 96 authoritative receiver registers;
8. require exact 96/96 same-machine Windows match;
9. E004t disables and powers off CSIPHY0;
10. require the sensor still suspended;
11. reboot immediately to Golden and retire the candidate.

Acceptance explicitly forbids any sensor stream callback, CSID/VFE stream callback, capture request, illumination, kernel warning/fault, or register mismatch.

One attempt only. No same-boot retry.
