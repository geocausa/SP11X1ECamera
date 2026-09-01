# E003h 0073 — steady IQ dynamics decomposition

Status: **accepted offline/static**.

Requests 4, 5 and 6 use the same normalized `0x958` command skeleton. Of 24 dynamic register fields, **16 are deterministic ping-pong bank selectors** and only **8 are calculated scalar values**. The calculated values are confined to DEMUX/BLS, PDPC and WB.

Between exact request5 and request6 only four DMI slices change: **LSC0, LSC1, GIC0 and GTM0**. PDPC, BPC/ABF, Gamma and DSX payloads are unchanged.

This reduces the producer problem to per-frame AEC/AWB/LSC/GIC/GTM interpolation plus deterministic bank parity; it does not require regenerating every field in the 0x958 packet.

No request6 Linux runtime is authorized by this checkpoint.
