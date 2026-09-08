# E003i BX — default SafeAgg optional-candidate zero state

Status: **PASS (static/offline)**.

BX closes BW's deferred absent-publication boundary for an uninterrupted ordinary `DefaultSequence` starting from AEC initialization.

The pinned DLL's SceneAnalyzer bank is a fixed 1000-slot array, each slot 24 bytes, rooted at bank-manager `+0x7d08`. Construction zeroes the entire `0x5dc0` bytes. `SetDataSceneAnalyzer` writes one complete 24-byte record to the same `base + dataID*24` layout.

A whole-tuning writer census proves that each optional SafeAgg value/confidence pair has only its own analyzer as writer:

- FaceSA: 37 / 36
- TouchSA: 48 / 47
- DepthSA: 138 / 137
- TrackerSA: 156 / 148
- SaliencySA: 189 / 188

None of those analyzers appears in the pinned normal `DefaultSequence`. Therefore, for an uninterrupted default-sequence preview beginning from initialized AEC state, all five candidate pairs remain exact zero by induction.

SafeAgg's method-11 input therefore reduces from 11 configured candidates to six active candidates: FrameSA, SatPrevSA, DarkPrevSA, BrightenImgSA, ExtremeColorSA and IlluminanceSA.

This checkpoint deliberately does not claim equivalence across a runtime sequence switch from face/touch/depth/saliency mode back to DefaultSequence. That transition can be handled separately if needed.
