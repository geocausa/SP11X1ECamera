# E003i-DQ — Windows AWB zero-weight fallback

Status: **PASS (static Windows oracle; no camera runtime).**

DP attempt1 exposed a previously uncaptured branch in the request-local AWB path: the saved G1 frame had eight P01 survivors, all eight received zero P04 weight, and the clean native trigger aborted on aggregate weight zero. DQ resolves that behavior directly from the pinned SP11 Windows `QcDeviceMFT8380.dll`.

Pinned Windows binary SHA256:

`c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`

The relevant CamX class is `CSAAGWV1`. Its accumulator at VA `0x1806d0dc0` multiplies the already-proven per-region weights and adds only positive accepted weights into object field `+0x58`; weighted X/Y sums are accumulated at `+0x4c/+0x50`.

The finalizer at VA `0x1806d1090` loads aggregate weight from `+0x58`. At `0x1806d10b4` it compares that float with zero. On equality it branches to `0x1806d10d0`, whose ARM64 instruction is `stur xzr,[x20,#0x4c]`: both X and Y are explicitly set to +0.0. Therefore Windows does not divide by zero, synthesize a fresh CCT, or return an algorithm failure for this condition.

Higher `CAWBMain::RunWBROIBased` logic at `0x180692c9c` then checks both computed decision-point coordinates. If either X or Y is <= 0 it takes the fallback block at `0x180692d7c`, which emits the diagnostic `Computed Decision Point ... previous AWB gains will be used`. The normal state-update stores at `0x180692cc0...` are skipped. Existing persistent AWB state is copied forward afterward.

Thus the production behavior for aggregate AGW weight zero is **hold previous AWB decision/gains**, not fail and not temporal-blend a synthetic zero target.

For the bounded Linux startup state, Stage AC already pins previous XY to `0x3f1129ca / 0x3f00e486`. P03 maps that held pair to float CCT bits `0x459c3ffb` = 4999.99755859375, published as 4999 by the already-proven FCVTZU/truncate rule.

No Windows boot was required because the branch and state-update suppression are explicit in the pinned production DLL.
