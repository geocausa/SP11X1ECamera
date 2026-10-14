# Reuse the FULL video RoundClamp configuration

The retained E006p packer, native front NV12 helper and upstream
sp11-front-fields.h already implement video rounding/clamping.
They are unchanged. The new internal wrapper removes both module-control
commands, validates the existing calibrated geometry policy, and requires
an explicit ten-bit video input declaration. It emits two ten-word
configuration commands,96 bytes, at0x9c70/0x9e70. It admits eight- or ten-bit
output; no new field algorithm or calibration is introduced.

The pinned original Titan680 packer0xb54b50 and builder0xb54810 run locally on
SP11 with owned synthetic partial contexts. Original instructions and PE
bytes remain immutable. The only intercepted helper is0x85ee78, observing
command arguments and returning success; the original command serializer
is not run. Fixed addresses come from the original builder, not replacement
address metadata. Constructors and a complete platform ABI are not claimed.

The request's0xf80 field selects the path; it is not output bit width.
The independent0x16cd8 field declares output bits. Video Full0, DS4 2,
DS16 3 use max(0,10-output_bits); pixel RAW8 uses14-output_bits.
These source calculations distinguish path domains. They do not establish
the live input precision or a CST12-to-video10 conversion. A numeric Gamma12
table tag alone is insufficient. The wrapper rejects input_bits12,14 and
undeclared output width0; a caller's ten-bit tag is a gate, not evidence.

110 original-source cases across three placements include18 admitted FULL
cases, distinct video/raw paths and a nonzero-image residual counterexample.
GCC/Clang ASan/UBSan each compare those18 cases,164 atomic rejections and
four compiled unsafe mutations. Caller SP/X19..29/D8..15 restoration,
image canaries, immutable request/output context and PE checks pass.
The original builder stores object+40 from the request path; that exact
owned store is allowed and its resulting metadata checked. Unsupported
original output declarations enter logging helpers outside this fixture
and are not accepted source cases.

Original zero-image module words0xc01/0x3c01 differ from the historical
helper's module-control policy. They are observed, not silently equated,
and neither module command is emitted. Zero software images and reserved
bits remain own policies, not hardware reset or inherited-profile proof.
No activation, crop, scaler, bus, DMI, camera, runtime install or blob-loader
replacement occurs. Existing unified48/libcamera21/run93/v15 is preserved.

Qualification:
- test-native.py <fresh-result-dir>; final source acceptance native05.
- build-worker.py; isolated native ARM64 W1/Werror compile only, no load.
- qualify.py; validates pins and writes derived metadata evidence.
- docs/FRONT-ROUND-CONFIG-20261014.json records boundaries and exclusions.

This adds20 independently specified configuration addresses to the catalog
(63 to83), not a complete precision-bound startup program. Both private
runtime consumers remain; upstream readiness remains false. Next bind the
original core/MNDS video domain to the own CST/Gamma policy and reuse the
retained scaler and measured CCM auxiliary state before fresh hardware parity.

The prior E006q MNDS23 scaler packer and E011DJ selected-bootstrap input
ledger were checked before proposing more work. The scaler calculation
already exists. Its old4064x2286-to3840x2160 fixture is for the rear camera;
it is not the selected front3840x2160-to2560x1440 mode. E011DJ explicitly
leaves complete independent startup and selected geometry/profile binding
open. Reuse the existing scaler algorithm; bind the front inputs and real
precision transition, rather than repeat the old rear fixture or claim
that offline replay already supplies the complete front startup.
