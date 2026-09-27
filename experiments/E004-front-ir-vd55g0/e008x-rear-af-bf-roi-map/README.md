# E008x — normal AF grid and BF ROI map source slice

Status: **SOURCE SHAPE / PRIVATE STRUCTURE PASS; AF RECTANGLE OPEN**.
Parent: E008w `c28e0342cdf79638c9ad4ba46efc12c916d0017d`.

The pinned same-SP11 DeviceMFT source gives the normal 5×5 BAF
`MapROIConfigure` arithmetic: its input rectangle and zero-overlap
tuning yield a single-precision cell size, integer-truncated to each
axis, with each ROI dimension one below the cell size. The valid,
non-clipping `BFStats25::ValidateAndAdjustROIBoundary` path retains
the left coordinate in its final store, rounds top down to even,
and decrements even dimensions to odd. The validator also has
scale, clipping, invalidation and overlap branches outside this
bounded source slice.

`af-bf-roi-map.h` implements only this generic offline transformation
with an explicit AF rectangle input. No captured coordinates or
request-specific constants are embedded. The synthetic C check
exercises odd vertical step rounding. The private same-SP11 audit
checks structural invariants of four normal/steady selector-1 payloads
(100 ROI records): all four have row-constant top, column-constant
left, even top, odd dimensions, and one vertical cell-step/parity
candidate consistent with height and relative row positions. This
**does not establish absolute coordinates or byte parity**. E008w's
75/75 normal width result and E008u's packet-0 300/300 result remain
the exact comparisons.

The earlier tentative 2336 vertical basis, used as a simple 25% AF
window with this mapper, fails the private relative row-shape test.
It was never source authority and must not enter the driver.

Source ownership of the missing input is now explicit:
`af_core_set_param` case 3 stores caller sensor/CAMIF geometry at
the AF state used by `af_util_get_roi_default`. The AF default
rectangle then passes through `af_util_adjust_roi` and
`BAFLogicDriver::SetROICoordinates` before the grid mapper.
Close those request-tagged geometry and coordinate transforms,
including the packet1-to-2 origin change, before supplying the
offline map or integrating any runtime path.

Run `cc -std=c11 -Wall -Wextra -Werror verify.c -o /tmp/e008x-verify
&& /tmp/e008x-verify` and `python3 audit-private.py` on SP11.
The latter emits only booleans and aggregate counts. No camera
module is built or loaded and no native rear runtime is authorized.
