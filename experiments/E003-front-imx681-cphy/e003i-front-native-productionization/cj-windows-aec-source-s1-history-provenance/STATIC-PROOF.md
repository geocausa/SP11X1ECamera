# E003i CJ static proof — analyzer S1 history provenance

Pinned DeviceMFT SHA-256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`.

## Manager history selection

`CAnalyzerManager`'s per-request update at `0x1803e3998` obtains a retained-history record before analyzer execution. It reads the history selector byte from `ModeInfo+0x8ec` and passes that value to `CAECXHistory::GetInternalFrameHistory` (`0x1803d3938`). CJ deliberately does **not** assign a constant value to that selector yet.

On the valid-history path the selected record contributes the seven retained exposure qwords at:

`+0x28,+0x50,+0x78,+0xa0,+0xc8,+0xf0,+0x118`

for `Short, Long, Safe, S1, S2, S3, S4` respectively.

## Exact source-vector writer

The same function converts those seven uint64 qwords to double and writes the AnalyzerManager state vector at:

`state+0x20,+0x28,+0x30,+0x38,+0x40,+0x48,+0x50`.

The key S1 pair is:

- `0x1803e3bb0`: load retained-history S1 qword from `history+0xa0` into `x25`;
- `0x1803e3ea8`: `ucvtf d16,x25`;
- `0x1803e3eac`: `stp d17,d16,[x9,#0x30]`, placing S1 at `state+0x38`.

## Analyzer consumption

`CAnalyzerManager::RunAnalyzer` passes `state+0x20` directly as `x1` to `CAnalyzer::RunAnalyzer` at `0x1803b2660..0x1803b2668`.

`CAnalyzer::RunAnalyzer` maps object `sourceType` and indexes that vector at 8-byte stride. BD has already proven ordinary Frame/Safe/Short/Long analyzers use `sourceType=S1`, lane 3. Therefore their source exposure scalar is exactly `state+0x20+3*8 = state+0x38`, i.e. the selected retained-history S1 qword converted to double.

## Correction to CI seam

CI exposed `source_exposure_s1` as if it were an independent request scalar. CJ proves that semantic boundary is too broad: on the ordinary valid-history path the value is derived from retained AEC history. The remaining reduction is temporal and lane-specific: prove the normal value of `ModeInfo+0x8ec` and prove/retain the post-T681 S1 history lane. CJ does not assume retained S1 equals retained Short.
