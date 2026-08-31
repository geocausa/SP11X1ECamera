# E003h 0052 — X1E front CSID link-derived clock rate

The corrected completed-frame boundary and HBI correlation expose a Linux-internal clock-selection defect before any further crop programming is justified.

For the proven front route, IMX681 reports one-trio C-PHY `link_freq=1.2GHz`. The existing CSID rate algorithm computes `link/4 = 300MHz`, adds the existing 5% CAMSS margin to 315MHz, then selects the first table rate strictly above that: 400MHz. X1E supplies exact 300/400/480MHz rates for both `csid` and `csid_csiphy_rx`.

But `csid_set_clock_rates()` applies that calculation only to legacy names `csi0..csi3`. X1E's `csid` and `csid_csiphy_rx` therefore fall through to `clk_set_rate(clock, freq[0])`, requesting 300MHz. X1E CAM_CC exposes distinct 300/400/480MHz source entries, so the request is not a rounding alias.

0052 is deliberately bounded to the proven front transport identity: X1E80100, CSID1, CSIPHY2, C-PHY, one trio. Only its `csid` and `csid_csiphy_rx` clocks enter the already-existing link-derived rate algorithm. All clock tables, margins, sensor metadata, CSID register programming, crop/RUP/AUP, VFE, RT-CDM, CSIPHY programming and DT are unchanged.

The resulting rate for the current front mode is 400MHz. The patch adds no MMIO access and no register value; its sole hardware behavior delta is a clock-rate request from 300MHz to the existing link-derived 400MHz choice on this exact route.

This is independently correlated by CSID HBI telemetry: Windows normal completed-frame HBI `0x03b203ad` gives halves 946/941; Linux error-time HBI `0x02c502c0` gives 709/704. Multiplying Linux by 400/300 predicts 945.33/938.67, within 1/3 ticks of Windows. A direct Windows 400MHz clock vote has not yet been observed, so this remains a strong causal candidate rather than production parity proof.

**No hardware runtime is authorized by this static checkpoint.** Package as a distinct Golden-safe one-shot candidate and perform a separate authorization review before any camera activation.
