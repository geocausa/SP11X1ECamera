# CAMSS single-pad TPG entity function correction

One line sets the retained TPG entity.function to MEDIA_ENT_F_CAM_SENSOR.
The retained TPG has one source pad and emits synthetic sensor data. The
same one-pad role is used by the GPL kernel VIMC sensor test generator.
CAMSS physical sensor-pad lookup follows enabled media links; all TPG links
remain disabled in this front-camera qualification. Probe03 explicitly checks
this and the immutable physical IMX681 -> PHY2 link.

The public Qualcomm TPG v8 proposal instead exports a two-pad formatter:
https://lists.openwall.net/linux-kernel/2026/01/13/635
That pad API is not transplanted into this retained one-pad implementation.
VIMC primary reference:
https://kernel.googlesource.com/pub/scm/linux/kernel/git/torvalds/linux/+/c7decec2f2d2ab0366567f9e30c0e1418cece43f/drivers/media/test-drivers/vimc/vimc-sensor.c

Patch GPL source classification only; no register, mode table, pad/link ABI,
stream operation or proprietary input changed. No author/DCO/acceptance claim.
Candidate27 is a module correction for the qualified full kernel26 ABI;
it is not a new full-kernel27 build. The copied private module root protects
installed26 and Golden modules. build-worker.py preserves101 parent pins.

Initial artifact lookup used the build tree; external-module Kbuild emitted
the module in the cloned source directory. The strict compilation succeeded.
Initial lookup error/raw diff checkpatch warning remain retained; final
artifact/config/vermagic/pins and described patch pass. QUALIFIED.json is
the definitive source-only result. No reuse of consumed hardware identities.

Candidate build:
02-kernel/upstream-ife-base-build-20261011-01/candidate-27/tpg-qual01
Evidence docs/UPSTREAM-TPG-ENTITY-VALIDATION-20261013.json.
Reproduction requires a fresh stage identity; do not overwrite this stage.
