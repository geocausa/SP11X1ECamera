# BLS121 configuration from retained native source and own calibration

The calibrated unified48/libcamera21/run93/v15 driver remains the integration
baseline. This package supplies its missing independently generated BLS
configuration block. It does not rebuild the driver, allocator, queue, IPA,
sensor mode or optical calibration.

## Prior work reused and exact gap

The previous cold-field package source-locks the BLS121 packer at0xb4bf30.
It proved the18-bit/bit14 and12-bit/bit20 layouts but did not execute the
constructor or tie a layout to the actual configuration address.

This slice executes the exact source constructor at0xa19140, then the same
packer and actual CreateCmdList at0xb4b980, with synthetic inputs only.
The source input context reads a selector at byte20 and the hardware-version
cell at0x17eb0 (an0x17000 base addition followed by0xeb0). The declared Titan680
value0x60800 is reused from the prior scalar-native proof. It is an owned
fixture, not a captured Windows context or a live hardware measurement.

The source parent scratch object is a bounded256-byte fixture. Its other
metadata is not claimed as a complete independently typed Linux ABI.
The constructor's two actual allocations are88-byte object and28-byte register
image. The latter starts entirely zero even when the allocator returns poisoned
bytes. There is no constructor, field, branch or packing shim.

| Source selector | Module address | Six-word configuration | Offset/threshold field |
| --- | --- | --- | --- |
| 13 | 0x4b60 | 0x4b68..0x4b7c | 18 bits shifted14 |
| 199 | 0x2260 | 0x2268..0x227c | 12 bits shifted20 |

Selector13 is thereby bound to the retained public VFE680 IFE BLS addresses.
The alternate block's wider pipeline identity is not claimed. The original
builder emits one module-control word, then six configuration words. This
compiler emits only the six configuration words; it emits no activation.

## Independently written compiler

sp11-front-bls121.h accepts typed offset18, gain17 and four threshold18 fields
in public THRESHOLD_CFG_0..3 order. It generates one fixed count6 REG_CONT
command at0x4b68,32bytes. Additional bits come from Linux-owned zero state.
Each field range, output size and input/output alias are checked before
publication. Registers, command types and addresses are not caller inputs.

The calibrated-default wrapper reuses the existing cold-policy validation and
own measured integer1649/gain0x835. Offset is1649<<2 in the18-bit field; the
two fractional bits are independently selected zero. Four cold thresholds are
zero, as in the proven source constructor before semantic packing. No colour
names are invented for their ordering.

The chosen fraction/threshold policy has not been qualified physically. Matching
an original constructor on synthetic inputs does not prove equality with an
old private tuning-dependent configuration. The live front BLS object/processing
precision is still unobserved. Geometry/tag validation alone is not domain proof.

## Validation

test-native.py executes original source on four owned fixture placements, with
nonzero poisoned allocations, allocation canaries, original image immutability,
bounded write ownership and actual SP/callee-saved register restoration.

712 IFE18 cases cover independent bits of offset/thresholds/gain, asymmetric
threshold order, measured defaults/fractions, boundaries and random vectors.
Eight alternate-selector cases independently verify the other address/layout.
The command observer checks the source builder's actual arguments. Its scalar
arguments are serialized into a synthetic oracle using the already qualified
GPL-compatible CDM format; the original packet serializer is not executed here.

GCC and Clang ASan/UBSan compile the actual new C header and compare all712
oracle vectors, including unchanged output tails. Invalid and late-invalid
fields, capacity, overlap, foreign geometry/selector/fraction and atomic
publication checks pass. Five compiled unsafe mutations are rejected:
wrong register, truncated gain, reversed thresholds, early publication and
bypassed calibration policy.

Only the bounded allocator and command observer/success status are intercepted.
No private profile, tuning file, camera frame/pixel/image hash or calibration
table is read. Original PE bytes and raw disassembly stay private on SP11.
The existing source
hardware-version input and packer anchors are pinned in the result.

A tiny module compiles against the prepared native7.1.5 ABI with W1/Werror and
zero diagnostics. It is never installed or loaded; CAMSS/kernel are not rebuilt.
Native01/02/03 attempts are excluded. They corrected verifier syntax and partial
input-context/parent-fixture bounds; no original source or hardware was changed.
Other modules' exploratory full constructors hit unmodeled CRT boundaries and
are not counted as acceptance evidence.

Run on SP11 with unique unused output directories:
- python3 test-native.py <unique-output-directory>
- python3 build-worker.py
- python3 qualify.py

Evidence: docs/FRONT-BLS121-20261014.json.

## Integration boundary

The previous24 measured words and five cold-policy words remain unchanged.
This block overlaps their BLS offset/gain and adds four threshold fields;
configuration candidates now cover33 unique addresses. No concatenated complete
startup, module activation or runtime loader replacement is implemented here.

Next reuse retained DEMUX/channel-gain/BLS common source and calibrated native
precision/geometry to complete independent functional startup around the
existing matrices/own LSC/ABF/tone/AE/AWB. Keep native transport/lifetime code.
Replace only private loading once surrounding setup is complete, then run a
fresh guarded physical qualification in the original calibrated domain.

Both installed private startup consumers remain, along with full pipeline/API
integration and whole-series provenance/license/DCO review. Upstream readiness
is false. Golden and the daily native branch stay protected.
