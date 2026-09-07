# E003i AU — Windows AEC frame ID / CamX request ID identity

Status: **PASS (static/offline) — on the normal CAECStatsProcessor → CAECEngine → CAECXControl path, AEC's algorithm `FrameID` is the same qword as the CamX request ID recorded by the stats processor.**

AT established that `PropertyIDAECFrameControl` is published/fetched without an extra property-pool request offset. AU joins the AEC algorithm's internal/logged frame coordinate to that CamX request coordinate.

## Pinned Windows oracle

`/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll`

SHA-256:

`c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`

## Request ID source

`CAECStatsProcessor::ExecuteProcessRequest` receives the request object in `x1`. It loads the qword at request-object `+0x8` and stores that exact qword at `CAECStatsProcessor+0x6008` (`0x1808358f8`). AT already pinned `+0x6008` as the request key later used by AEC publication.

Call this CamX request ID `P`.

## Request ID copied into the per-frame AEC block

The stats processor builds its per-frame AEC control block at `CAECStatsProcessor+0x6028` and calls the helper at `0x18083c108` with that block as `x1`.

Inside that helper:

- `x22` is the stats processor,
- `x19` is the per-frame block,
- `0x18083cc7c` reloads `CAECStatsProcessor+0x6008`,
- `0x18083cc88` stores it at per-frame-block `+0xeb8`.

Therefore:

`perFrameAECBlock.frameID(+0xeb8) = P`.

Immediately after the helper returns, `ExecuteProcessRequest` copies `0xee0` bytes from the per-frame block into the object held at `CAECStatsProcessor+0x18`. That object is the CAECEngine created during stats-processor initialization; the copy includes offset `+0xeb8` because `0xeb8 < 0xee0`.

## CAECEngine publishes the field as set-param type 40

`CamX::CAECEngine::SetPerFrameControlParam` begins at `0x180851410`. Its `this` pointer is preserved in `x20`.

At `0x180851524..0x180851534` it constructs one algorithm set-param record as:

- payload pointer = `CAECEngine+0xeb8`,
- payload size = `8`,
- set-param type = `40` (`0x28`).

The DLL's AEC set-param name table rooted at VA `0x181047f30` resolves table index 40 to the string `AECAlgoSetParamframeID`.

So the qword copied from CamX request ID `P` is explicitly passed to the algorithm as `AECAlgoSetParamframeID`.

## CAECXControl stores and prints the same qword

`CAECXControl::ControlSetParam` begins at `0x180379918`. Its jump table routes set-param type 40 to `0x18037ddd8`.

The type-40 case validates an 8-byte payload, loads its first qword, and at `0x18037de94` stores that qword into:

`CAECXControl + 0x16000 + 0x5d0 = CAECXControl+0x165d0`.

The AEC process-start diagnostic later loads `CAECXControl+0x165d0` at `0x18037219c` and prints it as:

`FrameID:%llu`.

Therefore, on this path:

`AEC algorithm FrameID = CAECXControl+0x165d0 = CAECEngine+0xeb8 = perFrameAECBlock+0xeb8 = CAECStatsProcessor+0x6008 = CamX request ID P`.

## Closed coordinate law

For the normal per-frame AEC path used here:

**AEC algorithm frame F and CamX request P are the same numeric coordinate: `F = P`.**

This closes the software-coordinate ambiguity. It does not by itself assign request `P` to an optical exposure interval; that downstream sensor-delay/latch boundary is handled separately.
