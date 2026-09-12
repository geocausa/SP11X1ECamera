# Camera ID — fresh unified-DTB rear-first R16 regression candidate

Status: **prepared / not installed / not armed / no runtime**.

ID is the fresh successor to retired IC. It keeps the same evidence-backed IB unified DTB and exact module set, but **does not reuse IC's boot identity**. IC never streamed; it exposed two harness defects before the attempt marker: discovery failed on `media-ctl` entity headers containing route counts, and the rear mutable route links were not explicitly enabled.

ID fixes both before another boot. The discovery parser is regression-tested offline against IC's real unified media graph. A dedicated route verifier proves that graph's initial rear mutable links are disabled and the front mutable route is untouched. During the one-shot attempt ID consumes the candidate **before any route mutation**, enables only `msm_csiphy1 -> msm_csid0` and `msm_csid0 -> msm_vfe0_rdi0`, verifies those exact links became enabled while the front route remains disabled, then configures the accepted rear formats.

The live contract is unchanged: one standard OV13858 color-bar frame with exact accepted SHA256, restore test pattern disabled, then 16 normal 4076x2806 packed-GRBG10 frames with sequences 0..15 and ~30 fps. Front streaming is forbidden. Any failure after the consumed marker is terminal for this boot; no same-stream/same-boot retry. Golden return, archive and retirement remain mandatory.
