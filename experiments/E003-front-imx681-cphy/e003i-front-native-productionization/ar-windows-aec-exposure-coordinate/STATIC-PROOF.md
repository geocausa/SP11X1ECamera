# E003i-AR static proof ledger

All addresses are VA/RVA observations from the SHA-pinned `QcDeviceMFT8380.dll` copied to the offline SP11 Linux analysis workspace.

## Object/callback identity

- Factory `0x1803a8be0` allocates wrapper object (0x1420 bytes), primary vtable `0x181338428`.
- Wrapper slot `+0x78` = `0x1803b38c0` (`RunConvProcesss`).
- Wrapper slot `+0xa0` = `0x1803b89f0` (`RunArbitration`).
- Adapter `0x1803a82d0` forwards wrapper `+0x78`; factory installs it at callback `+0xb0`.
- Adapter `0x1803a8280` forwards wrapper `+0xa0`; factory installs it at callback `+0xa8`.

## Arbitration input base field

Normal child calls through callback `+0xa8` with:

- `x1 = child+0xd0`
- `x2 = child+0x298 + lane*0x88`

`RunArbitration` stores `x1` in its context and AQ helper `0x1803c2500` reads `[x1+0x198]`.

Arithmetic identity:

`child+0xd0+0x198 = child+0x268`.

Producer at `0x18038a138` stores the base qword to `[child+0x268]`.

Immediately upstream (`0x18038a0c8..0x18038a138`) the value is formed from the selected bank body:

- correction factor: float32 `[table+0x00]`
- first knee pointer: `[table+0x20]`
- first gain: float32 `[firstKnee+0x04]`
- first time: uint64 `[firstKnee+0x08]`
- optional normalization coordinate: float32 `[table+0x10]`
- `FRINTA(gain*time*correction)`
- if normalization is nonzero: divide by the same `1.03f^normalization` helper
- clamp to at least 1
- store `[child+0x268]`

## Bank identity

Descriptor initialization at `0x1803a8f54`:

- descriptor offset `0xdcb0`
- type id `5`
- payload size `0x38`
- descriptor name pointer → literal `BankIDArbitrationTable`

The generic getter returns the bank payload. `RunControlArbitration` stores `returnedPayload+0x10` at `child+0x260`, hence `child+0x260` is the table body consumed above.

AQ's prior live scanner independently defined structural table `db = hdr-0x10`. The active T5 therefore has the same bank/header geometry: bank payload at `db`, table body/header at `db+0x10`.

`CAECXControlArbitration::CopyCustomExposureTable` provides a second producer of the same format. It copies its body into bank payload `+0x10` and explicitly zeros the body normalization field before the type-5/size-0x38 callback `+0x70` write at `0x180393a0c`.

For tuned symbol 681, the pinned serialized object contains correction factor `1.0`, a zero normalization word, count 4, and the knee-array reference immediately before the already-pinned four-knee byte sequence. The runtime loader expands serialized references/alignment, so this is supporting serialization evidence, not a claim of raw memcpy layout.

## Log-base initialization

Initializer `0x1800016d0`:

- loads literal at `0x180001700`: bits `0x3f83d70a` = float32 `1.0299999713897705`
- calls float logarithm-family implementation `0x180f5cd58`
- computes float reciprocal
- stores global `[0x181795000+0xa10]`

The adjacent initializer calls the same helper with exactly `2.0f` and stores the result at global `+0xa38`; the next tiny helper stores its reciprocal at `+0xa14`. Together with the helper's zero/negative/infinity domain handling and logarithmic range reduction, this identifies the cached `+0xa10` value as reciprocal log of `1.03f`.

## Coordinate producer

RunControlArbitration uses rounded exposure products and base `[child+0x268]`:

- converts product and base to float32
- float32 divide (`product/base`)
- converts ratio to double
- calls double logarithm implementation `0x180cc2e98`
- converts global reciprocal-log scale to double and multiplies
- converts result to float32

Two coordinates are stored at `child+0x208` and `child+0x230`.

With `RunArbitration x1=child+0xd0`, these are input `+0x138` and `+0x160` exactly.

## AQ reconstruction

At `0x1803b9594` RunArbitration loads input `+0x160`; at `0x1803b959c` it loads input `+0x138`. Explicit mode values may leave a candidate unchanged, replace it, multiply it, or add an offset. If the selected candidate differs sufficiently from its original coordinate, it calls `0x1803c2500` with that candidate in `s0`.

Helper `0x1803c2500`:

1. moves incoming coordinate to `s1`;
2. loads float32 `1.03f` (`0x3f83d70a`) into `s0`;
3. calls power implementation `0x180cf5a60`;
4. loads `RunArbitrationInput+0x198`;
5. converts base qword to double and multiplies by power result;
6. calls `0x1800014b0`, which is exactly `FRINTA d0,d0; ret`;
7. converts to uint64 `x3`;
8. loads table pointer from input `+0x190`;
9. calls `ApplyCoreTable 0x1803c35f8`.

## Arbitration → convergence bridge

- `RunControlArbitration` success return at `0x180389d2c` is `child+0x298`.
- Arbitration output records are 0x88 stride.
- `0x180389dd0` copies 0x50 bytes beginning at each output record `+0x30` into:
  - `child+0x688`
  - `child+0x6d8`
  - `child+0x728`
  - `child+0x778`
  - `child+0x7c8`
  - `child+0x818`
  - `child+0x868`
- `0x180389dd0` returns `child+0x688`.
- caller stores this at `main+0x14ca8`.
- normal callback `+0xb0` invokes `RunConvProcesss(main+0x14ca0, main+0x14cf8)`, whose input dereferences `main+0x14ca8`.

Therefore convergence consumes arbitration output-derived records and is downstream of arbitration.
