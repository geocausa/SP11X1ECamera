# E004k — scoped CSIPHY0 D-PHY Windows-parity CAMSS module

Status: **offline PASS; not runtime-authorized**.

E004k freezes the minimal CAMSS correction derived by E004j.

The module adds one read-only, default-off parameter:

`e004j_ir_dphy_windows_parity=1`

The gated behavior is consulted only when all of these are true:

- CAMSS version is X1E80100;
- CSIPHY id is 0;
- bus is D-PHY;
- the disposable parameter was explicitly enabled.

When armed, the receiver uses Windows live settle count `0x10`, restores the dynamic lane mask after the X1E gen2 table (IR receiver endpoint lane 0 produces `0x81`), and restores Windows common CTRL11..CTRL21 values `ff fe e6 df df fc fb 9b 7f bf ff`.

With the parameter false, existing D-PHY behavior is unchanged. Rear CSIPHY1 is outside the id-0 gate. Front RGB uses C-PHY and is outside the D-PHY gate.

The frozen module is byte-reproducible against Golden ABI at SHA256 `bc574b2027eee19fc07f12cb1c7efbd86ec1be38e09715878d035d89cb169eba`.

The shared kernel source was restored to its pre-E004k SHA after freezing the patch/module. `verify_e004k.py` replays the patch into a private temporary CAMSS tree and rebuilds it twice, proving the artifact can be reproduced without mutating the shared source tree.

No CAMSS module was loaded and no sensor stream occurred in E004k.
