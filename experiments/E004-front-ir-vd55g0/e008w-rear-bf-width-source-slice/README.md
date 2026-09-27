# E008w — BFStats25 normal ROI width source slice

Status: **OFFLINE NORMAL WIDTH 75/75 EXACT; OTHER GEOMETRY OPEN**.
Parent: E008v commit `9c62d70485f9dd706493cd8eee69cbd5f8e07af8`.

The exact same-SP11 `QcDeviceMFT8380.dll`
`BFStats25::ValidateAndAdjustROIBoundary` function at
`0x180a1f578` has a non-clipping branch that decreases an even ROI
width by one. E008w applies that narrow source-derived branch to the
25 normal AF seeds in packets 1, 2 and 3. It leaves packet 0 untouched,
and does not model the function's other boundary, scale, overlap, or
request-state branches.

`offline-roi.c` is a host-only extension of E008t's existing clean
semantic composer and E007e's clean DMI packer. `audit-private.py`
checks generated 300-byte selector-1 payloads against the pinned
private same-SP11 Windows corpus. It asserts packet 0 remains
300/300 bytes exact and all 75 normal ROI widths now agree. Normal
packets still mismatch in top and height for all 25 entries; packet 1
also mismatches in left for all 25. IDs and flags agree. Thus no full
normal selector-1 parity or native runtime authorization follows.

The private BFStats25 source also shows the validator is followed by
overlap/order handling and `UpdateHWROI` compaction. The AF default
ROI source reads CAMIF geometry at its own state offsets, whose
upstream assignment is visible in `af_core_get_param`. The next
source investigation must establish the request-tagged AF geometry
and coordinate transform through those stages; do not fit a captured
ROI basis or replay observed positions.

Run `python3 audit-private.py` on SP11. It emits only aggregate
field mismatch counts into `RESULT.json`; no captured values,
payload bytes, hashes, pixels, proprietary binaries, or private logs
are committed. No module build/load or camera runtime is involved.
