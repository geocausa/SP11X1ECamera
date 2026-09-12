# E003i-HW — production boot-bundle + fail-closed activation preparation

Status: **PASS / consumed / Golden-restored / retired**.

HW is the first production-style boot bundle built on the HV current-Golden DTB. The exact candidate is now installed under `/boot/sp11-7.1.5-camera-e003i-hw-prod-activation` but remains unarmed (`next_entry` empty). The candidate preserves the protected Golden kernel and initrd byte-for-byte and preserves the Golden kernel command line in order, changing only `sp11_entry` and adding the explicit camera-module blacklist plus fresh one-shot activation token. Unlike the historical disposable candidates it does **not** use `firmware_class.path=`.

The production package is current HR/HS authority (manifest `57aa9cc2...66a5a757`) while CAMSS and IMX681 modules remain exact HN binaries. Boot is fail-closed: camera modules are blacklisted, and `runtime-preflight.sh` requires the fresh token, candidate boot image, clean Git/origin, empty `next_entry`, exact installed HV DTB and intact package before `load.sh` may insert private modules.

If later authorized by the checkpoint sequence, `load.sh` is limited to module binding plus dynamic production topology discovery. **It does not stream.** There is no same-boot activation retry authority. Golden return and candidate retirement helpers are prepared in advance.

## Attempt 1 result

**PASS.** The fresh HW one-shot boot used the exact current-Golden-preserving command line and HV camera DTB, with camera modules initially blacklisted. Runtime preflight passed. Exactly one activation invocation then loaded the private HN `qcom-camss.ko` and `imx681.ko`, and production discovery resolved the accepted route at `/dev/media0`: `imx681 1-0010 -> msm_csiphy2 -> msm_csid1 -> msm_vfe1_pix -> msm_vfe1_video3` (`/dev/video7`, QC10C 3840x2160). No capture/stream helper was executed. Kernel health passed, no retry occurred, SP11 returned to protected Golden, and the candidate was retired.

Candidate boot ID: `2e35316b-ff57-489e-b7b0-d0ef661b530b`; Golden return boot ID: `6f2ce528-10bf-4eba-a0f6-68e9d8b7d556`. Archive: `/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-hw/attempt1-pass-production-activation-20260912T091444`; manifest SHA256 `c8c30d6269ab89c90d68ac98687f783a9845ca1982734c9d2e75868741bf67fd`.

This proves the **production activation path** on the current-Golden camera DTB. It does not yet prove a production stream on that merged DTB; the next gate is an offline one-stream acceptance policy before any new live candidate.
