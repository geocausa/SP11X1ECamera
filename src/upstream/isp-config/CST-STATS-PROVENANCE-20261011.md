# CST, row-sum and histogram geometry: source checkpoint

This slice completes the CST register encoding, adds enabled RSStats14 row sums
and implements the BHist16 region-count field. Inputs are explicit caller-owned
state. There is no tuning file parser, profile materializer, private schema,
file I/O, MMIO, DMA allocation or submission in the new production headers.
The installed front and rear private consumers remain.

## Provenance

The earlier project MIT semantic packers E006r/u/v define functional field
locations and encoding. Their source hashes are pinned in
`cst-stats-reference-20261011.json`. Reference comparison compiles those unchanged
functions with host-only type shims, on synthetic inputs; no tuning producer,
private oracle, Windows executable or profile is compiled, invoked or loaded.

The earlier E006r workflow obtained its **inputs** from a proprietary tuning
package. That producer and its values are excluded here. The new compiler takes
explicit matrices, offsets, signed auxiliary lanes and clamps, with no defaults
or import path. Test coefficients are the independently generated BT.601 matrix
from `open_config.py`; other vectors are numerical sweeps. Compatibility with a
functional packer does not establish open provenance for its old tuning inputs.

The field definitions remain trace-derived engineering facts. License and
provenance review is pending for a curated submission. This is independently
written GPL-2.0-only implementation, not a claim that proprietary material is
redistributable or that all functional semantics have upstream acceptance.

## Owned fields and bounds

| Block | Fields | Contract |
|---|---|---|
| CST | 0x6160 and eighteen words at 0x6168..0x61ac | Nine signed-13 coefficients, three signed-13 offsets, three signed-13 auxiliary lanes, three ordered 12-bit clamp intervals and explicit enable |
| RS | 0xbe60 and 0xbe68..0xbe70 | Contained ROI, conservative even origin, 1..16 columns, 1..1024 rows, 2..8192 cell width, even 2..16 cell height, explicit colour conversion |
| BHist geometry | 0xb26c only | Origin-zero even ROI, width >=4, height >=2, within active extents <=16384; counts generated from 2x2 regions |

CST deliberately excludes the 0x6164 gap. Coefficient words agree with the
existing sparse coefficient compiler. Offset/auxiliary lanes occupy bits31:19;
clamps occupy bits31:20. The auxiliary lane's exact mathematical role and the
source-owned camera policy for these lanes still require review. A complete
**encoding** is not a hardware-qualified colour-conversion configuration.

RS preserves the 0xbe64 gap. It floors cell width and floors cell height to even,
so uncovered right/bottom margins remain explicit policy. Sum shift derives from
cell area by integer bit counting. Register validity does not prove allocation
capacity, stats parser compatibility, anti-flicker policy or frame ownership.

BHist count fit and ROI containment are checked before encoding; dimensions that
the old helper would silently mask or clamp are rejected. This does not configure
BHist enable, colour channel selection, offset, bin/DMI bank/reset, buffer or parser.
Only one histogram register is owned. No old DMI-side zero-image words are reused.

## Composition and validation

`sp11-frame-fields.h` now takes a typed CST structure and explicit RS/BHist
geometry in addition to the existing matrix/round/scaler/BG inputs. It stages
656 bytes and owns 130 distinct registers, without duplicate writes. All errors,
including an invalid final histogram, leave caller output unchanged. This is
an internal source contract; no published ABI changes. Its command ordering is
not a qualified startup or per-frame transaction protocol.

Per compiler, synthetic vectors cover 12290 CST, 16490 RS and 16385 histogram
geometry cases. All 8192 signed offset/auxiliary values, all 4096 clamp values,
all RS count pairs, area-shift boundaries and all even histogram dimension field
values are tested. Bounds, containment, reserved bits, overlap, sparse register
ownership, short buffers and late composite errors are checked under GCC/Clang
ASan/UBSan. The prior 194 scaler/12297 BG cases and source regressions also pass.

Compile-only SP11 kernel stage `upstream-open-fields-20261011-04` passes
`W=1 KCFLAGS=-Werror` without warnings. The probe is not loaded and has no camera
integration. The public VFE880 reference now names the auxiliary lane SUBOFFSET, but its
SP11 interpretation and camera policy remain unqualified; see
`docs/UPSTREAM-OVERLAP-20261011.md` for hardware differences.

Source inventory coverage is 130 distinct fields /270 scalar occurrences;
2333 other mapped register occurrences need implementation or classification.
No runtime dependency has been removed, no capture/boot/runtime/module/DT change
occurs, and no readiness component is cleared.

## Concrete startup gaps

A new startup provider still needs a source-defined module graph, input
DEMUX/gains/black/WB/demosaic and CCM non-coefficient policy, any retained LSC/
denoise/gamma setup, required output bus/write-master and optional DS path
configuration, complete statistics enable/channel/buffer/parser contracts, and
source-owned DMI targets/banks/mappings. Unused vendor blocks can be omitted
only after their safe disabled state is established.

The provider must also establish startup/steady sequencing, frame identity,
atomic hardware updates, stop/error/DMA retirement and allocation lifetime.
Auxiliary CST lane meaning remains a prerequisite to choosing a real CST policy.
Neither the old instruction topology nor private scalar/table fallback is an
allowed way to fill these gaps. Only after integration/build review can a fresh
isolated hardware candidate be qualified with both private consumers absent.
