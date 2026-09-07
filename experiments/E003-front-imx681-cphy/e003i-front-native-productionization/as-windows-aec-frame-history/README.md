# E003i AS — Windows AEC temporal frame history

This checkpoint separates the true temporal `CAECXHistory` path from the `BankIDArbitrationTable` cache proven in AQ/AR and closes the normal steady-state previous-frame eligibility rule used by convergence.

## Pinned Windows oracle

`/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll`

SHA-256:

`c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`

## Proven layout and timing semantics

### Current stats frame ID

The routine containing `CAECXHistory::ModeInfo::SaveCurrentFrameID` begins at RVA `0x3b0680`.
It receives the new frame ID in `x1`, checks the existing valid ID, and stores:

- `ModeInfo+0x1c0`: current-frame-ID-valid flag
- `ModeInfo+0x1c8`: current **stats** frame ID

The diagnostic text is explicit:

`Current stats frame ID (%llu) is invalid, not larger than previous (%llu)!`

Thus this clock is the AEC stats-frame clock, not a guessed request counter.

### Relative history lookup

`CAECXHistory::GetInternalFrameHistory` is at RVA `0x3d3938`.
The requested history offset is passed in `w1` and narrowed to a byte. On the populated-history path it reads each saved record's first qword (the saved frame ID), adds the requested offset, and compares the result with `ModeInfo+0x1c8` (the current stats frame ID).

The accepted relation is:

`record.frameID + offset <= currentStatsFrameID`

Therefore for `offset=1`:

`record.frameID <= currentStatsFrameID - 1`

The convergence path at RVA `0x3b4708` passes exactly `w1=1`. If the lookup returns null it logs:

`AECXCONVRG no previous frame in history! Abort convergence`

So convergence's normal history dependency is explicitly previous-frame history. With contiguous stats IDs, the newest eligible record is F-1. With a gap, the dependency can be older, but it cannot be same-frame F through this lookup.

### History record and ring

Inside `CAECXCore::runEndOfFrame` (RVA `0x3bd280`) the embedded current history record is rooted at `core+0x10a8` and is copied as `0x1b0` bytes (432 bytes) into the history staging/node payload.

`CAECXHistory::SaveFrameToHistory` is inlined in this end-of-frame path. It allocates/recycles `0x1c0`-byte nodes: 16 bytes of list linkage followed by the 432-byte frame-history payload.

The payload's first qword is semantically proven to be the saved frame ID: it is compared against the already-saved frame ID and the failure path logs:

`Saved frame ID is too small! Skipping...`

The ring is bounded; once its count exceeds the configured maximum, the oldest entry is removed. The code also preserves a 432-byte fallback/archive copy before removal for the relevant flag state.

## Temporal law usable by the Linux replay

For a current AEC stats frame `F`:

1. `SaveCurrentFrameID(F)` establishes the current stats-frame clock.
2. Convergence requests history offset `1`.
3. The history lookup only admits records with `savedFrameID <= F-1`.
4. Normal contiguous operation therefore consumes F-1 as the previous-frame state.
5. `runEndOfFrame` packages/saves the current frame record for subsequent history use.

This closes the internal AEC history latency boundary. It does **not** yet prove the separate CamX property-pool / sensor-application request delay; that is the next boundary.

## Scope discipline

This checkpoint does not rename arbitrary history payload offsets beyond those statically proven above, and it does not conflate `BankIDArbitrationTable` type 5 with temporal frame history.
