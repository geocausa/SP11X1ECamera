# E003i CL static proof — self-fed S1 recurrence

Pinned DeviceMFT SHA-256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`.

## Temporal source identity

CJ proves `CAnalyzerManager` materializes analyzer `sourceExposure[S1]` from retained history lane S1 (`history+0xa0`). CK proves the ordinary front non-AutoHDR selector passed to `GetInternalFrameHistory` is exactly 3. Thus request `F` must use retained S1 from `F-3`.

CL removes CI's public `source_exposure_s1` field and performs:

`fi.source_exposure_s1 = history[F-3].s1_exposure`.

## S1 persistence producer

AX proves the normal Windows AEC feedback loop is seven lanes wide. `PopulateOutput` emits seven compact convergence qwords; post-convergence `RunControlArbitration(w4=0)` maps the selected lane through type-5/T681; `runEndOfFrame` persists seven rich retained qwords to seven history records.

S1 is lane 3 in the same seven-lane geometry used by CJ. Therefore its persisted value is the T681 retained qword for `convergence.linear[3]`, not Short lane 0.

CH implements the exact ordinary front-preview T681 retained qword:

`FRINTA(double(f32 gain) * double(exposureTime) * double(f32 correction))`.

CL applies that same verified primitive independently to `E003I_LANE_S1` and stores its `retained_exposure` as the history S1 field.

## Narrow retained state

The native state keeps only the history fields still consumed by the narrowed ordinary path: Short/Long/Safe, S1, and PredGain. S2-S4 are not exposed merely because Windows stores them; BS/BT/BU/CG have already removed them from ordinary convergence inputs, while CJ/CK add back only S1 for analyzer provenance.

The warm-up API seeds all four retained exposure fields. No S1=Short identity is assumed at seed time or during recurrence.

The verifier includes a deterministic temporal trap where `F-3.S1` and `F-1.Short` are deliberately different. It independently evaluates both candidate source paths, requires their final target publications to differ, and requires CL to match only the `F-3.S1` result. The randomized multi-frame corpus separately allows retained values to become numerically equal after T681; producer identity is not inferred from value inequality.
