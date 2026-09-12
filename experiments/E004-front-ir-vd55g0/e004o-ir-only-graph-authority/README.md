# E004o — IR-only CAMSS notifier graph authority

Status: **offline-only DT isolation stage**.

E004n proved that the native VD55G0 driver reaches the exact Windows sensor state and runtime-suspends cleanly, but CAMSS did not create the external sensor link because its async notifier was still waiting for the rear and front RGB endpoints advertised by the disposable DT.

E004o derives a strictly disposable IR-only DT from the proven E004l native-bind DT. It removes exactly four top-level graph participants:

- CAMSS external `port@1` (rear RGB);
- CAMSS external `port@2` (front RGB);
- the disposable rear OV13858 sensor node;
- the disposable front IMX681 sensor node.

Their endpoint subnodes disappear with those nodes. No internal CAMSS CSIPHY/CSID/VFE entity is removed.

The surviving IR graph remains byte-equivalent at the property level:

- sensor: `microsoft,sp11-vd55g0` at CCI0 bus0 address 0x60;
- sensor endpoint: D-PHY, one lane, 420 MHz, remote to CAMSS port 0;
- CAMSS port 0: D-PHY receiver lane position 0, remote to the IR endpoint.

This candidate is intentionally **not** a Golden promotion and does not alter the accepted rear/front work. It exists only to let CAMSS async-notifier completion occur with the IR sensor alone.
