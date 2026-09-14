# E004dn — repeated alternating RGB soak with Windows AWB fallback port

Status: **PREPARED / OFFLINE ONLY**.

E004dn is the fresh no-retry successor to E004dl. E004dl proved rear leg 1 but front leg 1 failed closed at G21 because Linux lacked Windows `CTrigleAdjV1` anti-cycle fallback. E004dm recovered and ported every reachable selector path for the pinned IMX681 profile, including the exact G21 `4 -> 36 -> 4 -> 36 -> 4 -> 36` visit-count / triangle-36 centroid resolution and ordinary boundary two-vertex projection.

This soak keeps the accepted unified RGB hardware authority byte-exact:

- unified IB DTB SHA `5e919d6bf778eb9eff5bf270447fa37f3c50ee16625c085c325e8d275d162321`;
- qcom-camss SHA `7afe6ed0bd0b945092256c53d111601c44cf33c174c1988945c05d8ef2697e95`;
- IMX681 SHA `ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6`;
- OV13858 SHA `13a8ad956075c518687149f8473764d85979f38a7666244b132ad992a9bc1309`.

Only committed front userspace is refreshed. The package is staged from `git archive HEAD:src/front-imx681` using those accepted module binaries. Expected package-manifest-file SHA is `60a3490177ef2befe61a61905160cec7e0b0b4d152fff4ccf5dccd8bca62cc1a`.

Planned one-shot sequence remains exactly:

`rear R16 -> neutral -> front R27 -> neutral -> rear R16 -> neutral -> front R27 -> neutral -> rear R16 -> neutral -> front R27 -> neutral`.

No same-boot retry is authorized. Every source must runtime-suspend before neutralization; all four mutable links must be neutral before enabling the next target. Final route must be neutral. Any production launcher `PINNED_FOR_REBOOT` condition causes immediate Golden return.

Linux SecureISP / VD55G0 are not touched by this RGB-only gate.

## Attempt 1 — PASS

The single E004dn candidate boot `63634d5b-01d8-4faa-922b-96a35322958e` completed the full six-leg sequence without retry:

`rear R16 -> neutral -> front R27 -> neutral -> rear R16 -> neutral -> front R27 -> neutral -> rear R16 -> neutral -> front R27 -> neutral`.

All five cross-camera transitions were accepted. Rear completed three 8-frame streams at ~30 fps and retained the exact accepted OV13858 color-bar SHA `6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346`. Front completed three 27-frame production streams with post-G3 policy `shadow`, zero later native writes, no DQBUF mismatch and no producer failure. Both sensors runtime-suspended after every leg; final topology was neutral; kernel-health checks passed.

The 72 live front AWB rows in this particular lighting run all remained in normal `triangle` selection mode. Therefore E004dn proves repeated cross-camera RGB robustness after the E004dm fix, while the newly ported centroid/two-vertex fallback itself remains covered by E004dm's Windows-authoritative offline G21 and boundary regressions rather than by this live lighting sample.

No same-boot retry was performed. SP11 returned to protected Golden FullIO v19c on boot `9dc8cdc6-d8d4-40fc-ba09-fdd7ab4ebace`, and the consumed candidate was removed from `/boot` and GRUB.
