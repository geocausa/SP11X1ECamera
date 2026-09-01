# Surface X1E IQ trigger semantics — 0073 static

The exact `QcDeviceMFT8380.dll` was decompiled around two authoritative functions:

- `IFELinearization33Interpolation::CheckUpdateTrigger` at RVA `0x94d6c0..0x94d8db`
- `IQSettingUtils::DumpTriggerCondition` at RVA `0x9a3fe0..0x9a4763`

This pins the X1E `ISPIQTriggerData` field offsets directly from the Surface binary. It also confirms that the common trigger vector entering the interpolation modules contains the AEC exposure time/ratio, sensitivity, real gain, lux index, AWB gains/CCT, DRC gain, lens position, LED state/ratio, geometry and black-level inputs needed by the IFE interpolation family.

## Structural interpolation map

Public Qualcomm CamX source is used only to label the shared interpolation architecture; Surface values and field offsets remain exact-binary/Chromatix authority.

- BPC/ABF41: DRC gain → HDR-AEC → AEC. The decoded Surface tree has three nested trigger levels and matches this structure.
- GIC31: HDR-AEC → AEC. The Surface tree has two trigger levels.
- GTM13: DRC gain → HDR-AEC → AEC (structural reference: GTM10).
- PDPC31: DRC gain → HDR-AEC → AEC (structural reference: PDPC20/PDPC11).
- Gamma15: DRC gain → HDR-AEC → LED → AEC → CCT.
- LSC41: lens position → DRC gain → HDR-AEC → LED → AEC → CCT.

The next oracle should capture the full X1E trigger struct at the exact Linearization33 `CheckUpdateTrigger` entry for requests 4, 5 and 6, and independently capture request6's DMI slot at the qccamisp request6 producer. No Linux request6 submission is permitted until an offline producer reproduces the Windows request6 output.
