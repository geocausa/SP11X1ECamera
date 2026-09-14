# E004dl — corrected bounded repeated alternating rear/front RGB soak

Status: **PREPARED / OFFLINE ONLY**.

E004dl is the fresh successor to E004dk. E004dk proved rear leg 1 and front leg 1 but failed in the harness while neutralizing the front route: it used CSID1 source pad 1. The accepted IH handoff authority and E004dk live topology both prove the mutable front PIX link is `msm_csid1:4 -> msm_vfe1_pix:0`.

E004dl changes only two harness mechanics:

1. front neutralization uses the proven CSID1 **source pad 4**;
2. `invoke-once.sh` enables Bash `ERR` inheritance (`set -E`) so failures inside leg functions always create the failure record.

The accepted camera artifacts, unified IB DTB, production front launcher, neutral-route policy, six-leg plan and no-retry rule are unchanged.

Planned single candidate:

`rear R16 -> neutral -> front R27 -> neutral -> rear R16 -> neutral -> front R27 -> neutral -> rear R16 -> neutral -> front R27 -> neutral`.

No candidate is installed or armed at this checkpoint. Linux SecureISP and VD55G0 remain outside this RGB-only test.

## Attempt 1 result

The corrected one-shot boot `b3d8fc82-f2ee-44e1-8343-8183ccbd9c62` consumed normally. Rear leg 1 passed and neutralized. Front leg 1 then reached the accepted R27 production path, but the live IQ producer encountered an RG/BG point outside the stateful `CTrigleAdjV1` mesh and deliberately failed closed. The capture subsequently observed a sequence-order mismatch and entered its designed `PINNED_FOR_REBOOT` state.

This is a **real front-production IQ boundary**, not the E004dk pad typo. No same-boot retry was performed. SP11 returned to protected Golden on boot `27b6ecc3-2ea6-42f4-840f-eaf3d46f3860`, and the candidate was retired.

Next work is to recover/validate the Windows-authoritative AWB mesh behavior for this out-of-mesh live point and fix the production front path without inventing a synthetic clamp. Only then should a fresh alternating soak be attempted.
