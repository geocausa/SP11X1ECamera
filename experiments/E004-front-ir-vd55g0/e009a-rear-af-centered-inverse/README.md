# E009a — centered AF ROI inverse consistency

Status: **PRIVATE INVERSE GEOMETRY PASS; FORWARD REQUEST INPUT OPEN**.
Parent E008z `6bb0c52a286e3df8750e97c24ab08b3491c95f39`.
Linux L4/L5 AF policy and BFStats25 ROI, original rear VideoRecord NV12
3840×2160. Evidence S for the pinned DeviceMFT operations, with the
retained same-SP11 original Windows selector-1 payloads as private P data.

`audit-private.py` searches only possible AF rectangle widths/heights;
it does not use captured coordinates as output constants. For each of the
four normal/steady payloads, it composes the direct centered default ROI
branch under explicit candidate CAMIF dimensions, the `af_util_adjust_roi`
even halfword step, the BAF vertical-grid-count-plus-11 height handoff,
`FUN_1806300a8` boundary clamp, E008x 5×5 float32 grid and BFStats25
valid nonclipping adjustment. It compares all 25 left/top/width/height
records privately. `RESULT.json` exposes only candidate counts/booleans
and possible absolute size-delta ranges.

With the accepted 4064×2286 active crop, each of four samples has **two
horizontal and two vertical AF-size candidates** that reproduce every
final ROI geometry field. Under the same direct path, the 4076×2806 raw
sensor extent and 3840×2160 video output dimensions have zero candidate
axes. Packet1 and packet2 candidate size sets are disjoint on both axes,
with a possible absolute AF-size change of 1–3 per axis despite equal
final ROI cell dimensions. Thus their uniform final-position shift can
arise from re-centering a slightly changed rectangle inside the same
quantized 5×5 cell sizes. This is a source-consistent explanation, not a
live request-stage observation or proof that those sizes were selected.

The accepted crop emerges as the only compatible geometry of these three
specific tested candidates under the bounded direct/default model. Other
CAMIF dimensions, AF branches, zoom/aspect adjustments, overlap/clipping
and striped scaling remain possible. The inverse search uses the final
Windows DMI as its fit target, so it is **not a predictive full-packet
byte-parity result**. E008u packet0 remains the only exact 300-byte ROI
payload. Do not wire E008z/E009a into native rear ISP runtime.

Next falsifiable gate: identify the selected loaded HAF default fractions,
CAMIF resolution and packet-specific ROI/zoom policy independently of the
final selector-1 payload; forward-compose those values and demand 300/300
bytes for each normal packet. A fresh Windows run is warranted only for a
specific intermediate field with a proven nonhalting observation method.

Run `python3 audit-private.py` only on SP11 with the private E006b corpus.
The script writes no coordinates, payloads, OEM tuning bytes or hashes to
its committed result.
