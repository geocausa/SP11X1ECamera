# E006q — Titan680 MNDS23 Video Full clean packer

Parent Git: `4730deaf` (E006p Crop12 + RoundClamp12 compile PASS).

Status: **STAGED / COMPILE-ONLY**.

## Goal

Implement the remaining 20 E006l startup-only MNDS23 registers from semantic Linux-owned geometry rather than captured Windows register words:

- Video Full luma: 0x9860..0x9884, 10 words
- Video Full chroma: 0x9A60..0x9A84, 10 words

## Source-lock

The pinned Surface `QcDeviceMFT8380.dll` Ghidra project source-locks:

- `CamX::IFEMNDS23Titan680::CreateCmdList`
  - Video Full luma: base 0x9860, count 10
  - Video Full chroma: base 0x9A60, count 10
- `CamX::IFEMNDS23Titan680::ConfigureVideoLumaRegisters`
- `CamX::IFEMNDS23Titan680::PackIQRegisterSetting`

The exact Titan680 normal-path arithmetic recovered statically is:

- phase scale = 2^21
- interpolation thresholds = 64 / 32 / 16
- phase multiplier = round(input/output * 2^21)
- for 1 < input/output < 2, phase-init and four-bit fractional compensation are derived from the same ratio
- input size and pre-crop coordinates are 14-bit fields
- the Video Full block is two contiguous 10-word luma/chroma sections.

The older public CamX MNDS implementation is used only for semantic naming/cross-generation interpretation; Titan680 packing comes from the pinned Surface binary.

## Private validation

The retained E006a startup representatives were reduced locally from SP7. Raw packet bytes and raw register words remain private.

Startup0 and startup1 independently reduce to the same semantic state:

- MNDS input: 4064x2286
- luma output: 3840x2160
- chroma output: 1920x1080 (2x2 subsampling)
- pre-crop: full input, 0,0 through 4063,2285
- module enabled
- stripe override disabled
- luma scale ratio: 127/120 in both axes
- chroma scale ratio: 127/60 in both axes

The clean semantic formula reproduces all 20/20 private MNDS23 words in startup0 and all 20/20 in startup1.

No captured register value, command byte or debugger address is committed.

## Contract

`camss-e006q-mnds23.inc` accepts dimensions, chroma divisors and pre-crop coordinates. It computes phase, interpolation and sub-2x compensation with integer arithmetic. The current implementation deliberately rejects stripe-override state with `-EOPNOTSUPP`; that path is not needed by the validated rear 4K startup and is not guessed.

The provider is retained only for compiler/type checking against E006m's `mnds23` callback signature. There is no runtime wiring, module load, camera access or RT-CDM submission.

Passing compilation closes packing/implementation for these 20 startup-only MNDS23 addresses. Production of the semantic geometry state and later guarded materializer wiring remain separate tasks.

Native rear Linux processed ISP remains **DENIED**.
