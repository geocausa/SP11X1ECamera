# Reuse front Video Full scaler configuration

Both existing E006q MNDS23 and sp11-geometry-stats.h already implement this
scaler. They are unchanged. The new internal wrapper binds only the existing
calibrated front3840x2160-to2560x1440 policy and emits18 configuration fields
at0x9864..0x9884/0x9a64..0x9a84,88 bytes. It removes top-level module words
and omits the separate Crop12 commands. Geometry arithmetic is not rewritten.

The pinned original Titan680 packer0xb4a140 and builder0xb48e10 run locally
with owned synthetic partial contexts and a zero software register image.
The actual Video Full path is metadata20=1, using image offset160 (luma)
and200 (chroma). Its command addresses are source-fixed0x9860/0x9a60 count10,
not supplied as replacement metadata. The source's float32 chroma divisors
at metadata12/16 are2.0, not integer bit patterns. Input dimensions come from
geometry0x3c/0x40, output dimensions0x64/0x68, and origin/end coordinates4/8/12/16.
Request0xf20 points to owned stripe context with flag0xd920=0.

The original FRINTA helper0x14d0 executes unchanged. Only command helper0x85ee78
is intercepted to observe arguments and return success; actual serialization
is not run. Source writes are bounded to its selected80-byte Video Full
image and named object metadata. Original PE and all arithmetic/branches
remain immutable. Caller SP/X19..29/D8..15 restoration, canaries, unchanged
request/geometry/stripe/descriptor and unused image slots are checked.
No constructor or full source platform ABI is claimed.

30 source cases cover24 comparisons over eight geometry tuples and three
placements, plus the selected mode's output-depth declaration sweep and a
nonzero-image residual counterexample. GCC/Clang ASan/UBSan each compare both
unchanged retained packers;3 calibrated-mode cases are admitted and21 other
geometries rejected.93 atomic negatives and four compiled unsafe mutations
pass. A tiny native ARM64 W1/Werror probe builds without installation/loading;
header style is0/0/0. Final source/native05 and native-compile01 are accepted.
Earlier source-image slot and host-type fixture failures are excluded.

Request output-depth declarations8/10/12/14 change no normal MNDS byte in
this owned fixture. Normal configuration0x600 matches the existing source
packer. Neither result establishes a named pixel-depth conversion or proves
the physical Gamma/CST-to-video precision chain. Gamma12 table representation,
CST12 policy range and video10 rounding remain distinct contracts. The full
candidate needs independent pipeline evidence and hardware qualification.

This adds18 addresses to the independent configuration catalog83->101,
not a complete startup program. Both installed private consumers remain.
Own calibration, unified48/libcamera21/run93/v15 and all existing source are
preserved. No profile/tuning/pixels are read, no camera or reboot occurs, and
no module/crop/bus/DMI/startup lifetime or loader is integrated.

Reproduction on SP11:
- test-native.py with a fresh output path.
- build-worker.py for an isolated compile-only stage.
- qualify.py to verify pins and save derived metadata evidence.

See docs/FRONT-SCALER-CONFIG-20261014.json. Next reuse retained Crop12 and
source core/Gamma precision evidence, bind the complete colour pipeline and
own CCM auxiliary fields, then integrate independent startup around proven
native lifetime before fresh hardware parity.
