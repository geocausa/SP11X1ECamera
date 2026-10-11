# Geometry and Bayer-grid compiler: provenance and limits

This third source slice adds geometry-generated MNDS23 scaler and FULL Crop12
commands, plus explicit AEC BE, tintless BG and AWB BG configuration. The new
production headers include only the project's open typed helpers. They read no
profile, private schema, file, captured register payload or calibration input.
No private profile was read during this implementation or its tests.

## Definition sources

The field definitions and integer formulae come from the project's earlier
MIT-licensed E006p/q/w/x/y semantic packers. Those sources explicitly embed no
captured Windows register words or command streams. Their functional layouts
were derived during the earlier reverse-engineering work; they are **not**
public Qualcomm GPL register documentation or proof of mainline acceptance.
The new implementation is independently written GPL-2.0-only source.
The exact test-only reference source hashes are in
`geometry-stats-reference-20261011.json`. The curated submission still needs
provenance/license review of trace-derived functional definitions.

| Block | Owned fields | Data producer |
|---|---|---|
| MNDS luma/chroma | Ten words each at 0x9860 / 0x9a60 | Active input and requested output dimensions, Q21 rounded scale ratios, interpolation thresholds, centred phase/fraction for the sub-2 downscale case, origin-zero input crop |
| FULL luma/chroma crop | Two words each at 0x9c68 / 0x9e68 | Inclusive origin-zero output height/width minus one; chroma half resolution |
| AEC, tintless, AWB BG | Eighteen words each at 0xb060 / 0xb660 / 0xb860 | Explicit ROI, counts, four thresholds, black reference, three weights, enable and quad-sync controls supplied by the caller |

The fixed scaler mode bits and BG all-sample mask are functional format controls,
not imported camera tuning. The compiler never imports cold/normal vendor
presets. Tests use synthetic thresholds/black/weights; these are not a calibrated
camera policy. BG channel thresholds retain the existing functional field order
and the repeated Gb threshold/minimum fields.

## Contracts

Geometry supports full-frame, origin-zero, single-stripe, even 4:2:0 downscale,
including the current front and rear dimensions. It rejects upscaling, odd or
zero dimensions, extents above 16384 and chroma ratios above 128. The ratio bound
prevents silent truncation of the phase field. There is no arbitrary crop,
stripe override, DSX, DS4/DS16, bus format or write-master setup.

BG validates ROI containment against the actual active region, even Bayer
origins, 1..64 counts, floor-to-even 16..512 cell sizes, 18-bit thresholds and
black reference and 7-bit weights. Flooring can leave uncovered right/bottom
margins; this is explicit Linux policy. A register-valid grid is not an allocated
statistics buffer: allocation layout, channels per cell, capacity and parser
agreement must be proved in the provider before any hardware use.

Individual compilers and the three-grid set preserve caller output on all errors,
including a bad last grid. `sp11-frame-fields.h` composes the previous colour and
rounding fields with these additions into a 568-byte fragment with 112 distinct
registers. It rejects overlapping input/output and does not mutate caller input.
Its temporary storage is bounded. The eventual provider must review total call
stack/context and resource lifetime.

The compositor's serialization order is a source contract, **not** a proven
hardware startup sequence or frame update protocol. It neither establishes frame
identity nor atomically applies registers to hardware. It has no MMIO, DMA,
allocation or submission.

## Validation and next gates

Synthetic tests cover 194 scaler cases, including both current camera modes,
interpolation boundaries and sub-2 phase initialisation, plus 12297 grid cases
per compiler. All count pairs 1..64, ROI containment, remainder flooring,
threshold/black endpoints, format bits, late errors, overlap, short buffers,
unique register ownership and fragment composition are checked.

Optional reference testing compiles unchanged hash-pinned MIT semantic functions
with host-only type shims. It compares all 24 geometry fields and all 54 BG
fields per relevant vector. Missing or changed references fail before compilation;
no fallback can substitute for the reference comparison. The portable no-reference
suite remains explicitly labelled as such.

GCC and Clang ASan/UBSan source tests and a separate SP11 kernel compile pass.
The probe is never loaded. The first build's missing module description warning
is preserved in its separate evidence; the corrected final build is recorded
separately. No boot, capture, runtime configuration or driver replacement occurs.

Source inventory coverage is now 112 unique fields / 230 scalar occurrences.
2373 mapped register occurrences remain unimplemented or unclassified; unused
vendor blocks need not be reproduced. Both installed private input consumers
remain. No readiness component is cleared.

Next resolve non-coefficient CST fields, active module graph/enables, minimal
black/WB/demosaic setup, histogram/row-sum/AF statistics and required output bus
configuration. Then bind independently generated tables to real kernel-owned DMI
mappings and assemble a complete startup provider without the old schema.
Review ordering, frame identity, stop/error/DMA lifetime before isolated hardware
qualification with both private consumers and fallback paths absent.
