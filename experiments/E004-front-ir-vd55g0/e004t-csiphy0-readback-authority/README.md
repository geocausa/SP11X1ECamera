# E004t — offline CSIPHY0 receiver-readback harness authority

E004t prepares the next bounded IR receiver gate. It does not run hardware.

The generated expected table is mechanically reconstructed from the exact E004j Linux write model and same-machine Windows CSIPHY0 live snapshot. The scoped E004k correction produces 96/96 modeled matches; E004t freezes those 96 offsets and full dword values as the runtime readback target.

The harness is receiver-only. On a future disposable candidate it will:

- dynamically resolve the native VD55G0 by OF compatible + address 0x60;
- require the sensor to already be runtime-suspended;
- follow the immutable sensor link to msm_csiphy0;
- require no enabled CSIPHY0 -> CSID downstream link;
- set only the CSIPHY0 sink format to Y10 644x604;
- call CSIPHY0 s_power(1);
- call CSIPHY0 s_stream(1), which programs receiver lanes through the pinned E004k CAMSS module;
- read all 96 programmed CSIPHY0 registers while powered;
- compare every full dword against same-machine Windows authority;
- call CSIPHY0 s_stream(0) and s_power(0);
- require the physical sensor to remain runtime-suspended.

The harness never calls the sensor's stream callback, CSID stream callback, VFE stream callback, capture APIs or illumination.
