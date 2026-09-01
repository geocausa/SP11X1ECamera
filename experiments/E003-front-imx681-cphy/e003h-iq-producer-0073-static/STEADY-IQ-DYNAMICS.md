# E003h 0073 — steady IQ dynamics decomposition

Status: **accepted offline/static**.

Requests 4, 5 and 6 use the same normalized `0x958` command skeleton. Of 24 dynamic register fields, **16 are deterministic ping-pong bank selectors** and only **8 are calculated scalar values**. The calculated values are confined to DEMUX/BLS, PDPC and WB, and all 8/8 are now independently reproduced.

At the captured Windows **wire** level, exact request5→request6 changes four DMI slices: **LSC0, LSC1, GIC0 and GTM0**. PDPC, BPC/ABF, Gamma and DSX payloads are unchanged.

The exact Surface binary now proves that the changing `GIC0` wire slice is not an independent calculated GIC LUT. `IFEGIC311::RunCalculation` writes the real GIC table at byte offset `0x18b8` (`0x62e` dwords × 4), and that logical 512-byte table is byte-identical between request5 and matched request6. Surface `IFEGIC311Titan680::CreateCmdList`, however, passes `0x62e` raw to `WriteDMI`, while LSC411 and GTM131 explicitly multiply their dword offsets by four. Packet patch serialization does not repair that unit mismatch.

Therefore Windows `0x4708` consumes bytes `0x62e..0x82e`: 326 bytes from the tail of LSC0 plus 186 bytes from the head of LSC1. See `GIC-WIRE-ALIAS-CLOSURE.md` and `gic-wire-alias-oracle.json`.

For Windows 1:1 parity, the remaining **independent** dynamic wire-LUT producer problem is now **LSC + GTM**, plus deterministic bank parity. The GIC wire payload follows automatically from the reconstructed LSC source alias. The unused logical GIC calculation can be reconstructed later for internal producer completeness, but it is not a hardware-wire parity gate.

No request6 Linux runtime is authorized by this checkpoint.
