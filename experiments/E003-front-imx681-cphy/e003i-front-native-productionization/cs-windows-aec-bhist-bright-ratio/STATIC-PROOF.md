# CS static proof anchors

## Tuning

`aecxmeteringstatscalculator` entry 162 is 396 bytes = five u32 header words + four fixed 23-u32 calculator records + `(55,7120)`.

The fixed records decode to:

- ID1 `AvgLumaBE16x16`, API1, `LumaBE16x16`, output 1..1.
- ID2 `FrameLuma`, API1, `LumaBE16x16`, output 2..2.
- ID3 `DarkRatio`, API5, `BhistY`, output 3..4; range entry 7111 = `(0,1000,0,1)`.
- ID4 `BrightRatio`, API5, `BhistY`, output 5..6; range entry 7118 = `(0,1000,255,256)`.

Bank4 dictionary entry 3334 maps data 5 -> `SaturateStatsAvg`, data 6 -> `SaturateStatsRatio`.

## Fixed runtime binder

`0x1803f44f8` binds fixed descriptor blocks at runtime-config offsets `0x28,0xa0,0x118,0x190` to calculator-manager slots `0x18,0x20,0x28,0x30` respectively.  Each descriptor is `0x78` bytes.

## Bank4 geometry and calculator publication

- getter case: `0x1803d5ef8..0x1803d5f24`;
- scalar read: `0x1803d5f04` computes `base + dataID*16`; `0x1803d5f0c` loads at `+0x3e8c`;
- `SetDataStatsCalculator @ 0x1803d6610`: `0x1803d6640..664c` copies a qword-sized 16-byte record to `+0x3e88 + dataID*16`;
- `CCalculator::RunCalculator @ 0x1803f4cb0`: `0x1803f63dc` loads `outputStart/outputEnd`; `0x1803f6484/6488` loads result lane `i`; `0x1803f64b8..64c0` publishes its Bank4 record.

## API5 / range kernel

API5 dispatch `0x1803f5380..53a0` passes mode `w3=0`, output pointer `calc+0x90`, calls `0x1803f6808`, and declares two outputs. API6 at `0x1803f53a4..53c4` uses mode `w3=1` and one output.

The common range kernel `0x1803ea478..ea9f0`:

- `0x1803ea570`: `ldp x22,x23,[record,#0x38]` gives raw-count and value-axis pointers;
- `0x1803ea56c/580`: bin count is capped at 1024;
- mode zero branches at `0x1803ea598 -> 0x1803ea72c`; literal `0x1803ea9fc` is exact float32 256.0;
- `0x1803ea76c` searches the supplied float axis;
- `0x1803ea840/85c/864` addresses a raw count and converts uint32 -> float32;
- the kernel accumulates interval count mass and value-weighted mass with fractional endpoints;
- `0x1803ea99c` divides weighted value mass by count mass (guarded by the kernel's epsilon/floor logic);
- `0x1803ea9c8` forms the normalized-CDF interval difference;
- `0x1803ea9cc` stores the two float outputs together.

## CDF preprocessing

`CAECXStatsHistProcessor::PreprocessCoreStats @ 0x1803f9758`:

- `0x1803f97e4`: raw count pointer `record+0x38`;
- `0x1803f97ec`: requires value-axis pointer `record+0x40`;
- `0x1803f9800`: per-source CDF base `+0x148`;
- `0x1803f9804/980c/9818`: first uint32 count -> float32 cumulative[0];
- `0x1803f9840..9888` and tail `0x1803f9898..98b0`: serial float32 cumulative construction;
- `0x1803f98bc..98ec`: denominator = `max(1.0f, final cumulative)`;
- `0x1803f9908..9958`: SIMD reciprocal-estimate/Newton normalization;
- scalar normalization tails use `FDIV` (`0x1803f9984`, `0x1803f99bc`).

## Raw parser

Existing Y pins BHist to 1024 x uint32. The SHA-pinned parser `0x1805f3c60` creates a `0x1018` parsed object. Ordinary parse loop at `0x1805f4090..40b0` masks every raw word with `0x01ffffff` before storage. Dual-source loop `0x1805f40e0..410c` masks both input words then adds them. The BHist constructor `0x180a06cc0` stores explicit bin count `0x400` at object `+0xe8`.

## Deferred fact

No CS proof identifies the producer of stats-record `+0x40`.  It is only proven to be a float32 value/luma coordinate array consumed by AEC histogram calculations.  Any exact raw-bin mapping remains deferred.
