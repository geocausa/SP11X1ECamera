# E009b — source-composed settled rear AF/BF ROI

Status: **OFFLINE PACKET0/2/3 + ONE STEADY SELECTOR-1 BYTE PARITY; PACKET1 POSITION OPEN**.
Parent E009a `e584710682d79af9d458b14af39edf6d0b8327a2`.
Linux L4/L5 AF policy and BFStats25 DMI, original rear color VideoRecord
NV12 3840×2160. Evidence S for source/tuning derivation and P for private
same-SP11 original Windows selector-1 comparison. No new physical run.

The selected pinned rear HAF tuning record contains a 25% pair at its
E008s-verified source locations. `offline-roi.c` composes that pair and
the accepted 4064×2286 rear crop through E008z's parameterized default
AF rectangle, the shown `af_util_adjust_roi` even-halfword step, BAF's
vertical-grid-count-five plus eleven handoff, the interior
`FUN_1806300a8` clamp branch, E008x 5×5 float32 grid and BFStats25 valid
nonclipping adjustment. It writes the resulting **source-generated**
geometry into E008t's independent per-packet BF semantic states and packs
selector 1 with the existing E007e code. Packet0 retains its distinct
hardcode seed. No captured Windows ROI coordinate or DMI byte is an input.

The private pinned corpus comparison yields:

| Request | Exact selector-1 bytes | Exact ROI geometry records | Boundary |
| --- | ---: | ---: | --- |
| startup0 hardcode | 300/300 | 25/25 | Prior E008u result retained |
| startup1 normal | 250/300 | 0/25 full; width/height 25/25 | All left/top differ |
| startup2 normal | 300/300 | 25/25 | Settled candidate exact |
| startup3 normal | 300/300 | 25/25 | Settled candidate exact |
| retained steady AC8 | 300/300 | 25/25 | One sampled steady payload exact |

Packet1's 25 left and 25 top fields alone differ; all its widths,
heights, region IDs and flags are exact. E009a's inverse audit shows its
positions are consistent with a centered rectangle under the same crop
whose pre-grid size differs slightly, while 5×5 cell sizes stay fixed.
The request-stage cause and selected packet1 inputs remain unproven.

This is **offline output parity for the named samples**, not proof that the
original loaded CamX HAF object reads the serialized 25% fields at the
same numeric offsets, nor proof of every steady frame or live Linux
operation. The E008z direct raw-offset mapping was invalid; here only the
known source-derived scalar pair is used and independently checked against
the private final payload. No native rear ISP runtime call site is added.

Next falsifiable gate: source-close packet1's AF state/ROI update order and
its first normal rectangle before BFStats25, then require 300/300 bytes
for all four startup packets from independently selected request inputs.
Only afterward revisit the remaining semantic seeds and the existing
native hardware/owner/DMA gates. Do not fill packet1 with a coordinate
literal inferred from final DMI.

Run `python3 audit-private.py` on SP11. It verifies the pinned tuning file
and emits only aggregate matches in `RESULT.json`. It builds host-only C;
it does not load a module, open a camera or export private payloads.
