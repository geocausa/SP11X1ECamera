# E004dq — rear RGB regression under unified RGB+IR authority

Status: **PREPARED OFFLINE / NOT INSTALLED / NOT ARMED**.

E004dp proved rear OV13858, front IMX681 and IR VD55G0 can bind simultaneously under the E004do three-camera DTB and the exact-lineage IR-gated CAMSS build, with Windows-exact CSIPHY0 receiver readback 96/96 and no stream.

E004dq is the next independent gate: prove the already-accepted rear R16 path remains byte- and timing-correct while front RGB and IR remain bound but unstreamed.

One fresh one-shot may:

- bind all three sensors;
- arm the same E004j CAMSS parameter, still scoped to X1E + CSIPHY0 + D-PHY;
- enable only rear `CSIPHY1 -> CSID0 -> VFE0 RDI0` mutable links;
- configure the accepted rear 4076×2806 GRBG10/QC10C path;
- capture one OV13858 color-bar frame and require SHA256 `6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346`;
- disable test pattern and capture exactly 8 normal frames, sequences 0..7, at the accepted ~30 fps envelope;
- return rear routing to neutral and require rear/front/IR runtime suspend.

It may **not** stream IMX681 or VD55G0, enable IR illumination, exercise CSIPHY0, invoke the E004t receiver harness, use Linux SecureISP, or perform any protected-memory action. In particular, the `E004J_CSIPHY0_DPHY_WINDOWS_PARITY` runtime marker must remain absent during rear-only streaming; its appearance would indicate incorrect gate scoping.

One attempt only; any post-consume failure returns to protected Golden with no same-boot retry.
