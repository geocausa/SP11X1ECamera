# Camera ID — fresh unified-DTB rear-first R16 regression candidate

Status: **PASS live rear regression / Golden restored / candidate retired**.

ID is the fresh successor to retired IC. It keeps the same evidence-backed IB unified DTB and exact module set, but **does not reuse IC's boot identity**. IC never streamed; it exposed two harness defects before the attempt marker: discovery failed on `media-ctl` entity headers containing route counts, and the rear mutable route links were not explicitly enabled.

ID fixes both before another boot. The discovery parser is regression-tested offline against IC's real unified media graph. A dedicated route verifier proves that graph's initial rear mutable links are disabled and the front mutable route is untouched. During the one-shot attempt ID consumes the candidate **before any route mutation**, enables only `msm_csiphy1 -> msm_csid0` and `msm_csid0 -> msm_vfe0_rdi0`, verifies those exact links became enabled while the front route remains disabled, then configures the accepted rear formats.

The live contract is unchanged: one standard OV13858 color-bar frame with exact accepted SHA256, restore test pattern disabled, then 16 normal 4076x2806 packed-GRBG10 frames with sequences 0..15 and ~30 fps. Front streaming is forbidden. Any failure after the consumed marker is terminal for this boot; no same-stream/same-boot retry. Golden return, archive and retirement remain mandatory.

The exact ID candidate is now installed under `/boot/sp11-7.1.5-camera-id-unified-rear-r16`, with Golden still saved and `next_entry` empty. Installed-unarmed state must be committed/pushed before arming.

## Live result

ID passed the unified-DTB rear regression exactly once. The candidate boot discovered both sensors, verified the rear route initially disabled and the front route untouched, consumed the attempt before route mutation, enabled exactly the two rear mutable links, then captured one 14,321,824-byte OV13858 color-bar frame with the accepted SHA256 `6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346` and 16 normal frames with sequences 0..15. Mean observed rate was 29.8393 fps. The rear sensor returned to runtime suspend, kernel health passed, no front stream occurred and no retry was performed.

Golden return passed on boot `1b77c56c-b54b-4c4a-a860-487c291ea83b`; the ID boot entry and boot directory were retired. Final archive manifest SHA256: `72c9c085e4e1960c185aa0672d9eac162d8487cea3a3c235bb716267c1110dad`. This accepts the rear path under the unified IB DTB and clears the next gate for a fresh front regression under that same unified authority.
