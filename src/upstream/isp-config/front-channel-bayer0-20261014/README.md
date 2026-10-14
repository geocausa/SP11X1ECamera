# Front Bayer0 pattern adapter: reuse fields and gain producer

This is a compatibility adapter around the previous CHANNEL_GAIN compiler,
not a new driver or calibration. The calibrated unified48/libcamera21/run93/v15
pipeline remains the baseline. The previous source Bayer2 fragment remains
unchanged and qualified in its declared domain.

## Audit before implementation

The retained front proof DEMUX-DGAIN-CLOSURE.md and DV README identify the
ordinary front common-setting branch as source Bayer0. The previous fragment
qualified Bayer2 using the retained rear scalar fixture. Matching gain words
alone did not establish equal Bayer pattern words.

Executing original common0x998e70 with synthetic Bayer0 input gives common
patterns0xac/0xc9. The original normal-slot packer0xb42840 places0xc9 at public
CFG0,0x3b68, and0xac at CFG1,0x3b6c. In contrast, source Bayer2 gives0xca/0x9c
in those registers. These are different patterns, not equivalent enums.

The same source calculation's four gains match the prior Bayer2 gain calculation
for all210 admitted synthetic producer comparisons. Thus the existing E012k
MIT arithmetic and actual native-front-params packing remain reusable in this
bounded, zero-channel-BLS, non-normalizing domain. The existing C producer
still declares Bayer2 and is compiled unchanged; that gain-output comparison
does not relabel its input enum or implement new front normalization behavior.

The separate DEMUX registers0x3960/0x3968/0x396c exist in the pinned public
VFE680 map. However, all274 register commands in the retained front replacement
inventory contain zero writes covering those three addresses, while five
commands cover CHANNEL_GAIN module0x3b60. This absence is scoped to that retained
inventory. It neither proves hardware reset/bypass behavior nor warrants adding
new separate DEMUX writes. The next action is actual core/precision/domain
binding using retained source, not speculative setup of an unused register block.

No private startup/profile/tuning file or optical data is read for this audit.
The prior front proof's vendor black-offset constants are deliberately excluded
from the adapter and synthetic validation; it uses only their source branch
identification and original executable-function identity.

## Minimal implementation

sp11-front-channel-bayer0.h uses the previous compiler for all field validation,
calibration policy, gain/offset packing, fixed registers and CDM encoding.
It stages that command, sets only the two source Bayer0 pattern words, then
publishes atomically. Outer input/output overlap and capacity are checked before
calling the staging compiler. No arbitrary register/packet/address interface
is introduced.

The cold wrapper reuses unity gains and zero channel offsets as an independently
selected candidate policy. Own measured BLS121 is separate. Physical equivalence
to inherited private startup, live Bayer routing and processing precision is
not established by this source proof. Geometry/tag alone remain insufficient.

| Pattern source | CFG0 at0x3b68 | CFG1 at0x3b6c |
| --- | --- | --- |
| Retained Bayer2 fragment | 0xca | 0x9c |
| Front Bayer0 adapter | 0xc9 | 0xac |

## Source qualification

test-native.py imports the unchanged prior native packer/builder fixture,
pinned to8b1fbceb4516d97b141f6cc9fdf3e3ff13fe0bdfa48c0fa5e81ac9ffa6183a0e.
Only its owned semantic input preparation changes Bayer2 to Bayer0. The original
common, packer, branches and field arithmetic are unchanged and executed on SP11.

927 source command comparisons on three placements include210 original common
producer cases and717 quantized bit/boundary/asymmetric/random states. Each
Bayer0 common gain result is also compared with the prior Bayer2 common.
Actual packer/builder SP and named callee-saved registers restore, source input/
metadata and canaries are unchanged. The common's four bounded writable
non-executable data cells run their original stores; other PE bytes/code stay
unchanged. A nonzero old-image counterexample remains checked.

GCC and Clang ASan/UBSan compile the actual adapter, prior field compiler,
unchanged E012k producer and actual native-front-params bridge. All927 commands
match the observed source builder arguments serialized with the qualified GPL
CDM format. Only PacketBuilder argument observation/success status is intercepted;
the original serializer and full constructor are not executed.

Invalid capacity/fields/policy/aliases and unchanged output tails pass.
Five compiled unsafe mutations fail under each compiler: Bayer2 pattern,
wrong pattern order, early publication, bypassed prior validation, missing
outer state overlap. Tiny native7.1.5 ARM64 W1/Werror compile and strict header
style pass with zero diagnostics. No CAMSS/kernel rebuild, module install/load
or camera access occurs. Acceptance directory is native02. Native01 passed source/compile but had
two header alignment style checks; native02 pins corrected whitespace.

Run on SP11 with unused output stages:
- python3 test-native.py <unique-output-directory>
- python3 build-worker.py
- python3 qualify.py

Evidence: docs/FRONT-CHANNEL-BAYER0-20261014.json.

## Remaining boundary

This changes two pattern values within the existing12-word candidate block;
it adds no register addresses. There are still45 unique configuration candidate
addresses, not a complete startup or submission-ready driver. No activation,
DMI, MMIO or runtime caller exists here; both private consumers remain.

Next audit/reuse the original front core-input/processing-precision/geometry
chain around these source Bayer0 fields and own measured BLS/colour domains.
Finish missing functional startup around existing own matrices/LSC/ABF/tone/
AE/AWB and the proven native lifecycle. Replace only private loading once
complete, then fresh guarded original-domain hardware/image-parity qualification.
Preserve Golden and daily source; no recalibration of an unchanged proven domain.
