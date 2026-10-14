# CST12 front candidate policy using existing encoders

The calibrated unified48/libcamera21/run93/v15 pipeline remains the integration
baseline. This package reuses the complete existing CST encoder and mathematical
generator. It adds only a configuration-only front policy around them.

## Prior solution and exact missing dependency

sp11-cst-stats.h already encodes all18 CST configuration words and the separate
module control. Its prior qualification compares unchanged E006r functional
packing on synthetic state and exhaustively tests offsets/auxiliary/clamps.
The encoder, sp11-front-fields.h, CDM helper and old tests remain unchanged.

run93 records measured own CCM, with no CST matrix override. The native optional
CST override only patches six matrix words; it preserves inherited offsets,
auxiliary lanes and clamps. Having that override function did not make complete
CST startup independent of the private carrier.

The new policy supplies explicit own fields rather than importing the old
rear/front tuning reserve. It is a mathematical candidate, not a claim of
equality with inherited front settings or a new optical calibration.

## Original source binding

The exact SHA-pinned same-SP11 DeviceMFT CST12 Titan680 packer0xb4d900 consumes
22 u16 fields: enable, three minima, three maxima, nine matrix values, three
offsets and three auxiliary lanes. Its object+32 points to the19-word image.
The original builder0xb4d390 emits module0x6160/count1, then0x6168/count18.
No register-address metadata is substituted: these are observed source arguments.

The source functions are identified by their CST12 Titan680 method strings and
stable RVAs in the pinned executable. The packet observer intercepts only
PacketBuilder0x85ee78 arguments/success status. No field, packing, branch or
arithmetic shim changes original instructions. The original packet serializer
and full constructor are not executed.

The owned initial image is zero software state. A nonzero-image counterexample
shows original packing preserves unnamed bits; neither a source constructor's
cold state nor hardware reset is claimed. The compiler owns complete words,
with other bits zero as independent policy.

## Independent front candidate

sp11-front-cst12-config.h accepts an explicit12-bit Gamma domain declaration,
the retained calibration geometry/tag policy and a typed CST state.
It reuses existing validation and sp11_cst_commands. It omits that helper's
first12-byte module-control command and publishes only80bytes at0x6168..0x61ac.
It emits no activation, disable command, DMI, MMIO, allocation or runtime call.

The admitted policy requires zero auxiliary/suboffset lanes, zero minima,
12-bit full-range maxima and zero luma/half-range chroma offsets. Nonzero
auxiliary lanes are rejected. Their exact mathematical placement in the
hardware datapath remains unqualified; the adapter does not guess it.

generate-policy.py calls the existing exact-rational bt601_q10_gbr() generator.
It derives the candidate matrix, input order G,B,R, neutral-preserving Q10
row sums1024/0/0, maxima(1<<12)-1 and offsets0/(1<<11)/(1<<11).
No vendor coefficient, reserve or tuning producer is used. The measured own
CCM and tone/LSC/ABF/AE/AWB sources are not modified or refitted.

| Candidate property | Basis and limit |
| --- | --- |
| Gamma output12-bit | Existing working own tone bridge emits12-bit base/delta; its endpoints span0..4095 |
| CST mathematical range | Explicit independent12-bit full-range candidate, not observed live precision |
| Matrix | Existing rational BT.601 generator in G,B,R order |
| Auxiliary lanes | Zero only; nonzero hardware role not inferred |
| Output offsets/clamps | Powers-of-two range policy, encoded with existing source-bound fields |
| Activation | Excluded; parent must assemble and qualify startup order |
| Final NV12 | Existing10-to8 helper does not automatically establish12-to8 compatibility |

A numerical bit-depth tag is a caller declaration, not proof of the actual
Gamma/CST/core/scaler/rounding chain. This candidate must not be appended
blindly to the old10-bit minimal program or a live calibrated stream.

## Validation

675 original packer/builder comparisons use three fixture placements.558
matrix/boundary/asymmetric/random cases match the complete encoder and the
new admitted configuration.117 source-valid offset/auxiliary/clamp states
match the generic encoder but reject atomically under the new policy.
All original image bytes, inputs and object metadata remain unchanged apart
from owned image writes; canaries, actual SP and named callee-saved registers
restore. Original PE bytes/disassembly remain on SP11.

GCC and Clang ASan/UBSan compile the actual existing encoder and new adapter.
Capacity, aliases, late bad coefficients, foreign policy/domain/enable and
unchanged output tails pass. Four compiled unsafe mutations fail: wrong
configuration slice, early publication, foreign precision and bypassed
calibration policy.4096 mathematical neutral values preserve luma and chroma
centre in the integer model; this is not actual ISP rounding/image proof.

The generated policy is checked against the existing rational generator.
Tiny native7.1.5 ARM64 W1/Werror compile and both headers' strict style pass
without diagnostics. Final acceptance is native02/native-compile02. Native01
host compilation caught signed-offset versus unsigned-constant comparison;
native-compile01 had passed. Final source uses the matching signed expression.
No original encoder or original executable code was changed.

On SP11, with unused stages:
- python3 generate-policy.py --check
- python3 test-native.py <unique-output-directory>
- python3 build-worker.py
- python3 qualify.py

Evidence: docs/FRONT-CST12-POLICY-20261014.json.

## Remaining work

This selects18 additional configuration candidate addresses:45->63. It is
not a concatenated complete startup program and does not remove either installed
private consumer. The existing3072-byte own Gamma leaf stays unchanged.

Next reuse retained output/scaler/RoundClamp source to bind the selected12-bit
Gamma/CST range to final8-bit NV12; do not inherit the10-bit helper's assumption.
Complete core, measured CCM auxiliary state and other startup around the proven
native lifecycle, then replace only private loading in a fresh isolated candidate.
Original-domain physical/image parity and whole-series provenance/API review
remain. Golden/daily driver and existing calibration are preserved.
