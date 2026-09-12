# Camera IC — unified-DTB rear-first R16 regression candidate

Status: **installed / not armed / no runtime**.

IC is the first live candidate using the IB unified rear+front DTB. Its only runtime question is whether the already-accepted rear OV13858 path still works when CAMSS is the private front-production module and the platform uses IA's conservative unified IOMMU fwspec. Front IMX681 may bind so the unified async graph completes, but **front streaming is forbidden in IC**.

The one-shot regression reproduces the accepted rear contract in one consumed attempt: configure `OV13858 -> CSIPHY1 -> CSID0 -> VFE0 RDI0`, capture one standard sensor color-bar frame and require the exact accepted SHA256, restore test pattern disabled, then capture 16 normal 4076x2806 packed-GRBG10 frames with sequences 0..15 and accepted ~30 fps timing. Teardown, sensor runtime PM, kernel health, Golden return and candidate retirement are mandatory.

There is no same-stream or same-boot retry. Preparation was committed/pushed before installation. The exact candidate is now installed under `/boot/sp11-7.1.5-camera-ic-unified-rear-r16`, `next_entry` remains empty, and installed-unarmed state must be checkpointed/pushed before arming.
