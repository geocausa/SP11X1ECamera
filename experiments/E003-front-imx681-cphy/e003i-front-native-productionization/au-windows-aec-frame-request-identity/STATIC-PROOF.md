# Static proof anchors

Pinned DLL SHA-256:
`c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`

## A. CamX request ID

`CAECStatsProcessor::ExecuteProcessRequest` starts at `0x1808356e0`.

- `0x180835708`: preserve incoming request object (`x20=x1`)
- `0x180835820`: load request qword `[x20+0x8]`
- `0x1808358e8`: reload `[x20+0x8]`
- `0x1808358f8`: store that qword at `CAECStatsProcessor+0x6008`

## B. Per-frame block gets the same ID

`ExecuteProcessRequest`:

- `0x180835af4`: materialize per-frame block offset `0x6028`
- `0x180835af8`: `x26 = processor+0x6028`
- `0x180835afc`: helper arg `x1=x26`
- `0x180835b04`: helper arg `x0=processor`
- `0x180835b08`: call helper `0x18083c108`

Helper:

- `0x18083c12c`: `x22=x0` processor
- `0x18083c138`: `x19=x1` per-frame block
- `0x18083cc7c`: load processor `+0x6008`
- `0x18083cc88`: store qword to per-frame block `+0xeb8`

Back in `ExecuteProcessRequest`:

- `0x180835b14`: destination object = `[processor+0x18]`
- `0x180835b20`: copy size `0xee0`
- `0x180835b24`: source = per-frame block (`x26`)
- `0x180835b28`: copy call

Since `0xeb8 < 0xee0`, the request-ID field is included.

Stats-processor initialization stores the created CAECEngine object at `CAECStatsProcessor+0x18` at `0x180833a00`; nearby diagnostics identify the creation path as `CamX::CAECEngine::Create`.

## C. CAECEngine passes +0xeb8 as frameID

`CamX::CAECEngine::SetPerFrameControlParam` entry: `0x180851410`.

- `0x18085144c`: `x20=x0` (`this`)
- `0x180851524`: payload size = `8`
- `0x180851528`: upper 32-bit set-param type = `0x28` / 40
- `0x18085152c`: payload pointer = `x20+0xeb8`
- `0x180851534`: store `{payload, size/type}` set-param record

AEC set-param name pointer table root: `0x181047f30`.

Index 40 entry VA: `0x181048070`; it points to `AECAlgoSetParamframeID`.

## D. Type 40 becomes CAECXControl FrameID

`CAECXControl::ControlSetParam` entry: `0x180379918`.

Jump-table type 40 target: `0x18037ddd8`.

- `0x18037ddd8`: payload size field
- `0x18037dddc`: require >= 8 bytes
- `0x18037de88`: load payload pointer
- `0x18037de90`: load first payload qword
- `0x18037de94`: store to `CAECXControl+0x165d0`

AEC process-start diagnostic:

- `0x180372190`: form `CAECXControl+0x16000`
- `0x18037219c`: load qword at `+0x5d0`
- format string: `CID:[%d] ====== AEC Process start, CamID:%d, Role:%d, FrameID:%llu ===========`

Thus the printed/algorithm FrameID is the same qword that originated as the CamX request ID.
