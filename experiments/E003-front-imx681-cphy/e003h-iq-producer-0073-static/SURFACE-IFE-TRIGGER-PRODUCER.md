# E003h 0073 — exact Surface IFE trigger producer boundary

The exact Surface `QcDeviceMFT8380.dll` primary IFE request path is now pinned.

- `CamX::IQInterface::IQSetupTriggerData`: RVA `0x88a4e8`.
- Primary caller: `CamX::IFENode::ExecuteProcessRequest`.
- IQ setup call: RVA `0x746e6c`.
- Geometry update call: RVA `0x746f14`.
- **Complete trigger hook:** RVA `0x746f18`.

At the complete hook the per-request `ISPInputData` remains at `x26 + 0x1ef8`. Its exact Surface `frameNum` is at `+0x1ff8`, therefore `qwo(x26 + 0x3ef0)`. The trigger block starts at `+0x2080`, therefore `x26 + 0x3f78`.

The `frameNum` offset is independently proven by the exact Surface `ProgramIQConfig` decompile, which logs `param_2[0x3ff]` as the request/frame number.

This gives a deterministic Windows oracle hook that captures **request ID + fully populated AEC/AWB/AF/sensor trigger vector atomically**, rather than correlating a module-level trigger callback by timing.

No Linux request6 runtime is authorized by this checkpoint.
