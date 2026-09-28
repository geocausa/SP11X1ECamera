# E009c — request-scoped AF rectangle to BFStats25 handoff

Status: **OFFLINE PACKETS 2/3 EXACT; PACKET 1 AF INPUT OPEN; NO RUNTIME**.
Parent E009b `00340ab17c6c5ff681e1294c0bf612e1e612c371`.

`af-request-roi-handoff.h` accepts the AF-selected rectangle for a specific
normal rear request, applies the source-derived even adjustment and BAF
height increase (five vertical grid cells plus eleven), requires the verified
interior clamp branch, maps 5×5 ROIs and updates only that request's isolated
E008o/E008t BF selector-1 semantic state. It rejects packet0, invalid or
consumed state, and geometry that would need an unmodeled clamp. Its temporary
map makes failed requests leave the packet state unchanged. There is no CAMSS
include or hardware call site.

The host harness generates default AF rectangles from the selected 25% HAF
pair and accepted 4064×2286 crop, seeds four independent E008t packet
states, and writes only normal selector-1 payloads to a local private audit.
The private same-SP11 comparison is 300/300 bytes for startup2 and startup3,
250/300 for startup1 (its 25 left and 25 top fields differ). The packet0
hardcode state is independently preserved. The first normal request's selected
AF rectangle, ROI type/update and zoom or tuning policy have not been
observed. A derived packet1 rectangle must not be embedded as a driver seed.

Source owner: pinned DeviceMFT `af_util_get_roi_default` RVA 0x628630,
`af_util_adjust_roi` RVA 0x628AB0, `BAFLogicDriver::SetROICoordinates`,
`MapROIConfigure` RVA 0x6301C8, and BFStats25 valid adjustment. AF sensor
info parameter case 3 replaces the packed CAMIF dimensions at AF state
+0x1fd00 per request and preserves prior dimensions at +0x1fd28. The current
request can select other AF ROI paths. The handoff intentionally requires
that upstream policy to supply its rectangle.

Run `cc -std=c11 -Wall -Wextra -Werror -fsanitize=address,undefined
compile-check.c -o /tmp/e009c-check && /tmp/e009c-check >/tmp/e009c-roi` for
an offline structural check. `python3 audit-private.py` verifies against the
private on-device corpus and writes only aggregate counts to `RESULT.json`.
Neither operation loads a camera module or uses MMIO/DMA.

Next: independently observe or source-derive first normal request's AF
selection before BFStats25, then inject the request-specific rectangle and
require four startup selectors exact. Other AEC/AWB/LSC/GTM semantic seeds and
native VFE IRQ/DMA generation-safe ownership remain separate runtime gates.
