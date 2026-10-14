# Normal-slot channel startup configuration using retained producers

The calibrated unified48/libcamera21/run93/v15 driver is the integration
baseline. This package adds the missing independently generated CHANNEL_GAIN
startup words. It preserves the existing producer, per-frame bridge, optical
calibration, queues, allocator, transport and IPA.

## Prior work and exact compatibility gap

E006z already established four-Q10 gain packing. E012k supplies the MIT C
producer; native-front-params.h supplies the actual GPL per-frame packing.
Both are compiled unchanged in this qualification. The existing E011AI Native
class supplies the original scalar calculation at0x998e70; its private live
validation main function is never invoked. No new gain algorithm is written.

Those components did not independently emit the surrounding startup pattern
and channel black-offset registers. The public VFE680 header names CHANNEL_GAIN
at0x3b60, with configuration0x3b68..0x3b94. The separate DEMUX block at0x3960/
0x3968/0x396c is not silently substituted for this block.

Original DemuxBLS141 packer0xb42840 and builder0xb41ff0 are executed locally on
SP11 with synthetic input. The normal descriptor has slots0/0, common pointer
at+16, command buffer at+80 and zero request metadata at+0x2018. Its source
object has image pointer at+32. Module/configuration addresses at+80/+84 are
Linux-owned public metadata, not captured vendor values; the full constructor
and its binding to a live front object are not executed or claimed.

For source Bayer2 and period0, the existing common calculation supplies pattern
words0x9c and0xca. The packer puts0xca in public CFG0 and0x9c in CFG1.
The existing native bridge calls its admitted front pattern Bayer0; equivalence
between these enum/domain labels is not established by identical gain packing.

| Configuration register | Independently typed input |
| --- | --- |
| 0x3b68 / 0x3b6c | Source Bayer2 normal-slot patterns0xca /0x9c |
| 0x3b70 | Q10 channel0 in upper16, channel1 in lower16 |
| 0x3b74 | Q10 channel3 in upper16, channel2 in lower16 |
| 0x3b78..0x3b84 | Four input offsets,14bits shifted18 |
| 0x3b88..0x3b94 | Four output offsets,14bits shifted18 |

Offset register order is public CH0 even, CH0 odd, CH1, CH2. Source common
u16 cells10/12/14/16 supply output offsets and11/13/15/17 input offsets.
The original packer preserves lower unnamed bits from its old image. A
nonzero-image counterexample explicitly demonstrates that. The new compiler
chooses a zero initial image; this is an independent policy, not a statement
that inherited bits or physical reset state were zero.

## Compiler and policy

sp11-front-channel-gain.h emits one fixed count12 REG_CONT command,56bytes.
It admits four nonzero Q10 gains up to0x7fff, matching the existing bridge,
and eight14-bit offsets. Capacity, field bounds, input/output overlap and the
retained original calibration policy are checked before output publication.
It has no arbitrary register, address, packet type, DMI, MMIO or runtime caller.

The cold wrapper chooses unity Q10 gains and zero channel offsets. Existing
own BLS121 subtraction is separate. No vendor-derived602/593/592/596 offsets
or private profile/tuning defaults are imported. Unity/zero here is a candidate
startup policy; equality with the previous private startup is not claimed.
Original sensor/processing precision, Bayer mapping, geometry and optical
parity must be qualified before applying it around the existing calibration.

E012k is reused only with synthetic zero channel BLS and non-normalizing gains.
Its admitted vectors remain below the original31.999 gain normalization
boundary. This test does not extend its floating-point normalization behavior.

## Qualification

The native04 acceptance run executes927 packer/builder cases on three owned
placements:210 use the unchanged native common and prior C producer,717 cover
independent gain bits, all input/output offset bits, boundaries, asymmetric
order and deterministic random state. Original packer/builder instructions
are unchanged and bounded. The builder's command arguments are observed at
PacketBuilder0x85ee78; only its success-return boundary is intercepted.
The existing GPL CDM format serializes those arguments into the oracle;
the original packet serializer is not executed.

Actual SP and callee-saved integer/floating registers restore, source fixture
metadata and inputs stay unchanged, and image canaries remain intact. The
original common itself writes four bounded non-executable writable .data cells.
Those original stores are allowed, not patched or intercepted. All other PE
bytes, including executable sections, remain unchanged. Original PE bytes
and raw disassembly stay on SP11.

GCC and Clang ASan/UBSan compile the actual new header, unchanged prior producer
and actual native per-frame bridge. All927 output commands match. Tests also
check field rejection, capacity, aliases, foreign domain/selector/fraction,
unchanged output tails and atomic publication. Five compiled unsafe mutations
fail under both compilers: wrong pattern, gain order, offset shift, early
publication and bypassed policy.

A tiny W1/Werror module compiles against native7.1.5 ARM64, with zero diagnostics.
It is not installed or loaded. There is no CAMSS or kernel rebuild.
Strict header style reports0 errors/0 warnings/0 checks.

Acceptance is native04. The earlier attempt with a missing parent stage,
native01's overly broad whole-image immutability assertion, and native02's
redundant incompatible host endian typedef, and native03 register-enum
arithmetic (actual X29 was omitted) are excluded. They changed only
the verifier, never original instructions or hardware.

On SP11, with unused output directories:
- python3 test-native.py <unique-output-directory>
- python3 build-worker.py
- python3 qualify.py

Evidence: docs/FRONT-CHANNEL-GAIN-20261014.json.

## Remaining work

This adds12 unique configuration candidate addresses to the previous33:
45 total, not a complete startup program. There are no module activation
commands, complete front precision/Bayer binding, separate DEMUX setup or
private loader replacement here. Both installed private consumers remain.

Next audit/reuse the retained separate DEMUX0x3968/0x396c routing and original
front precision/Bayer/geometry source. Continue the surrounding startup using
own matrices/LSC/ABF/tone/AE/AWB and the proven native lifecycle. Once complete,
replace only private loading and perform fresh guarded physical qualification
in the original calibrated domain. Whole-series standard API integration and
provenance/license/DCO review remain; upstream readiness is false.
