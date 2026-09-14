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
