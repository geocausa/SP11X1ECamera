# Handoff after CT

CT closes the ordinary raw-BHist adapter required by the native AEC effective-analyzer path. It converts generation-tagged 1024-bin `BhistY` plus LuxIndex and the already-retained F-3 `{Safe,S1,PredGain}` history state into Bank4 `{6,7,8,19}`.

The Windows value axis is reproduced byte-for-byte, the parser's `0x01ffffff` count mask is applied, and the 1024-bin CDF normalization mirrors the Windows ARM reciprocal/Newton path.

The runtime-descriptor oracle is important for integration: ordinary front `BhistY` has runtime flag1 for BrightRatio, SatPrevHighPCTLLuma, and DarkPrevLowPCTLLuma, but flag0 for ShortSatPrevHighPCTLLuma. With source tag `3=S1`, the flag1 weighted-luma cap uses retained F-3 `Safe/S1/PredGain`. In CT's required outputs this materially affects Bank4:7 and :8; Bank4:6 is the CDF-mass lane and is invariant, while Bank4:19 uses the fixed 0.98f cap.

## Next checkpoint

Integrate `native-bhist-bank4.{c,h}` into the existing native AEC request-loop/raw-stat boundary. The integration should pass the selected ordinary F-3 history entry directly:

- `safe_exposure` -> CT history Safe;
- `s1_exposure` -> CT history S1;
- `pred_gain` -> CT history PredGain, including the proven synthetic startup `+0.0f` case (which produces an exact zero flag1 luma cap on Bank4:7/:8).

Then generation-tagged STATS3A should feed the already accepted CR/CI/CL/CP recurrence/analyzer path without externally supplying Bank4 `{6,7,8,19}`.

Keep the next checkpoint offline first. A new Linux camera runtime remains unnecessary until the complete raw-stat → Bank4 → native AEC integration is mechanically joined and verified.

## Durable state

- Branch: `experiment/e003-front-imx681-cphy`.
- Parent checkpoint before CT: `580ca98`.
- Golden kernel: `7.1.5-sp11-render-parity-v4+`.
- GRUB saved entry: `sp11-audio-fullio-v19c`; `next_entry` empty.
- Runtime descriptor oracle was read-only FrameServer process memory; no process writes.
- Earlier KDNET S1 breakpoint was cleared before its return.
- No new Linux camera runtime, STREAMON, sensor write, or camera MMIO was performed by CT.
