# X1E CSID clock / HBI correlation

This gate closes a Linux-internal clock-selection defect before proposing another camera run.

For the proven front transport, the sensor reports fixed C-PHY `link_freq=1.2GHz`. `csid_set_clock_rates()` computes a CSID minimum of link/4 plus 5% margin: 315MHz, which selects 400MHz from X1E's 300/400/480 table. But the scaled branch recognizes only legacy clock names `csi0..csi3`; X1E calls its clocks `csid` and `csid_csiphy_rx`. They therefore take the generic branch, which requests the first table entry, 300MHz. X1E CAM_CC exposes distinct 300, 400 and 480MHz source rates, so this is not a rounding alias.

Independent format-measure telemetry correlates almost exactly with the same ratio. Windows normal completed-frame HBI is `0x03b203ad` (halves 946/941), while Linux error-time HBI is `0x02c502c0` (709/704). Scaling the Linux halves by 400/300 predicts 945.33/938.67, within 1 and 3 ticks of Windows; both ranges retain width 5.

This proves Linux requests 300MHz where its own link-derived algorithm requires 400MHz and makes the clock delta a strong causal candidate for the completed-frame crop failure. It does **not** claim a directly observed Windows 400MHz clock vote; Windows 400MHz remains correlated rather than directly proven. No hardware runtime is authorized by this static result.
