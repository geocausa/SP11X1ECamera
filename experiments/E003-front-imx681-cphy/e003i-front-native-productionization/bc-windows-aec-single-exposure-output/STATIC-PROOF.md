# Static proof anchors

## `ConvergeSensorExposures` — `0x1803d13f0`

- `0x1803d141c`: load Short log from `+0xa0`.
- `0x1803d142c`: initialize current exposure count/index to `1`.
- `0x1803d1448`: seed internal s1 `+0x100` from Short.
- `0x1803d144c..0x1803d1474`: compare index 1 with `min(activeExposureCount,4)`; for count 1, multi-exposure loop is skipped.
- `0x1803d1574..0x1803d159c`: fill remaining sensor slots from the first slot; for count 1 this yields `+0x108,+0x110,+0x118 = +0x100`.
- `0x1803d1788..0x1803d17d8`: copy internal `+0x100,+0x108,+0x110,+0x118` to normal s1..s4 `+0xb8,+0xc0,+0xc8,+0xd0`.

## RunConv loop-back

- `0x1803b67e4`: call `ConvergeSensorExposures`.
- `0x1803b67f0`: branch back to `0x1803b6080` common output path.
- `0x1803b63f0`: common path calls `0x1803cdf50`.

## `CAECXConvergence::PopulateOutput` — `0x1803cdf50`

Reads seven doubles at:

`+0xa0,+0xa8,+0xb0,+0xb8,+0xc0,+0xc8,+0xd0`

and writes seven qwords at:

`+0x00,+0x08,+0x10,+0x18,+0x20,+0x28,+0x30`.

Each lane calls the common power helper with exact base literal at `0x1803ce3f8` = `1.0299999713897705`, followed by `FCVTZU`.

## Joined checkpoints

`verify-bc.py` fresh-runs:

- AX — convergence/history/T681 recurrence;
- AQ — table681 selector/replay;
- AV — IMX681 `2/2/2`, maxPipeline 2 delay record;
- AW — request-F sensor packet submission/KMD scheduling boundary;
- AP — retained bounded live group-held IMX681 sensor-control evidence.
