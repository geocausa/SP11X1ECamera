# E004j — CSIPHY0 D-PHY Windows receiver authority

Status: **PASS / offline receiver comparison only**.

E004j closes the lane-number ambiguity with same-machine evidence.

The live Windows IR stream used CSIPHY0 in TwoPhase/D-PHY mode with one data lane and raw lane mask `0x81`. The exact X1E Linux CSIPHY encoder defines the D-PHY clock-enable as bit 7 and encodes each data lane as `BIT(data_lane_pos * 2)`. Therefore:

```
clock bit 7 = 0x80
data lane position 0 = BIT(0) = 0x01
0x80 | 0x01 = 0x81
```

So Windows mechanically maps to **Linux receiver data lane position 0**. The E004 receiver-side CSIPHY0 endpoint is already `data-lanes=<0>`. The sensor-side endpoint remains `<1>`, matching the convention already used by the accepted rear sensor; CAMSS consumes its own receiver endpoint.

## Current Linux receiver mismatch

The exact X1E D-PHY table is already very close to the Windows receiver state. Modeling the current Linux write order against the 8 KiB live Windows CSIPHY0 snapshot gives **79/96 exact matches**.

All 17 mismatches are confined to three causes:

- five settle-count registers: Linux computes `0x12`, Windows live is `0x10`;
- Linux first writes the correct dynamic lane mask `0x81`, then `lane_regs_x1e80100[]` overwrites common CTRL5 at `+0x1014` with hard-coded `0xD5` (clock + all four data lanes);
- generic D-PHY cleanup zeros common CTRL11..CTRL21 at `+0x102c..0x1054`, while Windows retains `ff fe e6 df df fc fb 9b 7f bf ff`.

A correction scoped strictly to **X1E80100 + CSIPHY0 + D-PHY** that uses settle `0x10`, restores the dynamic lane mask after the gen2 table and retains the exact Windows common-control values models to **96/96 register matches**.

This scope deliberately leaves accepted rear CSIPHY1 D-PHY and front-RGB C-PHY unchanged.

## Polarity

CAMSS stores parsed lane-polarity fields, but the exact X1E gen2 CSIPHY implementation never consumes them. No polarity override is needed to reproduce the full set of receiver registers Windows programmed. E004j therefore does not make a separate electrical-polarity assertion.

No CAMSS runtime or sensor streaming is authorized by this stage.
