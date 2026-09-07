# Static proof anchors

Pinned binary SHA-256:
`c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`

## SaveCurrentFrameID

Function region: `0x1803b0680`

Key anchors:

- `0x1803b06a8`: `mov x21, x1` — incoming current stats frame ID
- `0x1803b06ac`: load `ModeInfo+0x1c0` valid flag
- `0x1803b06bc`: load `ModeInfo+0x1c8` previous/current stats frame ID
- `0x1803b06c0`: compare previous/current ID against incoming ID
- `0x1803b0738`: diagnostic format `Current stats frame ID ... not larger than previous ...`
- `0x1803b0740`: function label `CAECXHistory::ModeInfo::SaveCurrentFrameID`
- `0x1803b0764`: store incoming ID at `ModeInfo+0x1c8`
- `0x1803b076c`: set `ModeInfo+0x1c0 = 1`

## GetInternalFrameHistory

Function RVA: `0x3d3938`

Key anchors:

- `0x1803d3958`: `uxtb w19, w1` — requested relative history offset
- `0x1803d39e8`: test `ModeInfo+0x1c0` current-ID-valid state
- `0x1803d3a78`: load history-buffer depth/count byte
- `0x1803d3b3c`: load `ModeInfo+0x1c8` current stats frame ID
- `0x1803d3b44`: load saved record first qword at node payload `+0x10`
- `0x1803d3b4c`: add requested offset to saved record ID
- `0x1803d3b50`: compare `(savedFrameID + offset)` with current stats frame ID
- `0x1803d3b54`: `b.ls` accepts the record when the sum is `<=` current stats frame ID

Thus `offset=1` implies `savedFrameID <= currentStatsFrameID-1`.

## Convergence caller

At `0x1803b4700` convergence sets `w1=1`, loads the history object, and at `0x1803b4708` calls `GetInternalFrameHistory`.
If null, the path emits `AECXCONVRG no previous frame in history! Abort convergence`.

This gives the semantic name of offset 1 independently of the container implementation.

## End-of-frame save

Function RVA: `0x3bd280`, identified by the in-function `CAECXCore::runEndOfFrame` label.

Current embedded history payload:

- root: `core+0x10a8`
- payload size: `0x1b0` / 432 bytes

Save mechanics:

- `0x1803bd5c4`: destination staging `+0x230`
- `0x1803bd5cc`: copy size `0x1b0`
- `0x1803bd5d0`: source is current embedded history payload
- `0x1803bd5f0`: allocate `0x1c0` bytes for list node
- `0x1803bd60c..618`: copy 432-byte payload into node `+0x10`
- `0x1803bd6e8..6f8`: compare saved record frame ID with current record frame ID
- `0x1803bd748`: diagnostic `Saved frame ID is too small! Skipping...`
- `0x1803bd750`: function label `CAECXHistory::SaveFrameToHistory`
- `0x1803bd7c8`: allocate another `0x1c0` node on the alternate recycle path
- `0x1803bd7e4..7f0`: copy `0x1b0` payload into node `+0x10`
- `0x1803bd818..874`: enforce bounded ring size and unlink/free oldest record

No claim is made here about CamX request-property delay or sensor latch delay.
