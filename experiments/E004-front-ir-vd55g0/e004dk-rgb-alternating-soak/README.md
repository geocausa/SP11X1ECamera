# E004dk — bounded repeated alternating rear/front RGB soak

Status: **PREPARED / OFFLINE ONLY**.

Parent authority is Camera IJ: exact unified IB DTB plus pinned production CAMSS, IMX681 and OV13858 binaries. E004dk targets the one remaining RGB integration blocker in IJ: repeated alternating same-boot switching.

The planned single one-shot candidate runs exactly six production legs with no retry:

`rear R16 -> neutral -> front R27 -> neutral -> rear R16 -> neutral -> front R27 -> neutral -> rear R16 -> neutral -> front R27 -> neutral`.

Each rear leg captures eight normal 4076x2806 RAW10 frames; leg 1 also rechecks the accepted exact color-bar hash. Each front leg runs the accepted production R27 launcher with post-G3 policy `shadow` and 27 frames. Every source must reach runtime suspend before its route is neutralized. All four mutable links must be neutral before enabling the next target. Final state is neutral before reboot to protected Golden.

The candidate reuses exact accepted artifacts by hash; it does not rebuild alternate camera binaries. Linux SecureISP and VD55G0 are not involved in this RGB soak.

No candidate is installed or armed by this prep checkpoint.

## Attempt 1 result

Attempt 1 was consumed on boot `fa8221e5-ab6b-4a8a-a944-8c66eb32fff6`. Rear leg 1 passed, including the exact accepted OV13858 color-bar hash, then neutralized successfully. Front leg 1 also completed and reached runtime suspend. The harness then disabled `CSIPHY2 -> CSID1` correctly but attempted `CSID1:1 -> VFE1 PIX:0`; `media-ctl` rejected it with `EINVAL`. The accepted IH handoff script and the captured live topology both prove that the mutable PIX link is `CSID1:4 -> VFE1 PIX:0`.

This is therefore a **harness failure, not a camera-stack failure**. No same-boot retry was performed. SP11 returned to protected Golden on boot `9abd8ab6-657e-49aa-bd8c-6a59789a52f9`, and the failed candidate was retired.

A second harness defect was identified during failure handling: Bash `ERR` inheritance was not enabled for shell functions. E004dl must use `set -E`/`errtrace` so any future function failure records its failure object automatically.

E004dk is frozen here; its consumed attempt namespace will not be reused.
