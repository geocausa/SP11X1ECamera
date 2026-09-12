# Camera IC — unified-DTB rear-first R16 regression candidate

Status: **consumed pre-stream harness failure / Golden restored / candidate retired**.

IC is the first live candidate using the IB unified rear+front DTB. Its only runtime question is whether the already-accepted rear OV13858 path still works when CAMSS is the private front-production module and the platform uses IA's conservative unified IOMMU fwspec. Front IMX681 may bind so the unified async graph completes, but **front streaming is forbidden in IC**.

The one-shot regression reproduces the accepted rear contract in one consumed attempt: configure `OV13858 -> CSIPHY1 -> CSID0 -> VFE0 RDI0`, capture one standard sensor color-bar frame and require the exact accepted SHA256, restore test pattern disabled, then capture 16 normal 4076x2806 packed-GRBG10 frames with sequences 0..15 and accepted ~30 fps timing. Teardown, sensor runtime PM, kernel health, Golden return and candidate retirement are mandatory.

There is no same-stream or same-boot retry. Preparation was committed/pushed before installation. The exact candidate is now installed under `/boot/sp11-7.1.5-camera-ic-unified-rear-r16`, `next_entry` remains empty, and installed-unarmed state must be checkpointed/pushed before arming.

## Attempt 1 outcome

The IC candidate boot reached module bind but **no camera stream occurred**. `discover-unified.py` failed because its media-entity regex did not accept the current `media-ctl` header form containing route counts, so the rear sensor list was empty. Read-only graph inspection then exposed a second harness gap: the mutable rear links `msm_csiphy1:1 -> msm_csid0:0` and `msm_csid0:1 -> msm_vfe0_rdi0:0` were disabled after load, while IC's invoke helper never enabled them.

No runtime-output directory, consumed marker, STREAMON, dequeue, or front stream existed. The candidate boot is therefore classified as **pre-stream harness failure, not a camera/driver failure**. The boot identity is retired anyway; there is no same-boot reuse. Golden return and candidate retirement passed. Archive manifest SHA256: `90392180610bbed064718631fb84d2aaa9912136874b02abe056d0117c683b90`. A fresh successor identity must fix and offline-prove both harness issues before any new boot.
