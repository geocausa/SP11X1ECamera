# E006l — rear startup register ownership and phase partition

Parent Git: `3ed95452` (E006k startup symbolic compose PASS + continuation checkpoint).

Status: **STATIC/OFFLINE OWNERSHIP PASS**. No camera runtime, module load, MMIO write, reboot, or new Windows oracle run was performed.

## Goal

Turn E006k's fully symbolic startup MAINs into an implementable producer contract without importing captured Windows register values.

A private-vs-safe comparison was performed **locally on SP7**:
- private source: retained E006a selected representatives;
- public/safe source: committed E006h steady symbolic recipe downloaded from GitHub;
- output: `STARTUP-VS-STEADY-SAFE.json`, containing only register classes/counts/offset lists and **no raw values**.

No private E006a bytes were moved into Git.

## Exact 714-register partition

Every unique startup register belongs to exactly one disjoint class:

- **468** — `STEADY_SINGLETON_REUSABLE`: startup value is byte-identical to the one committed steady singleton observation in every startup occurrence.
- **25** — `STEADY_DYNAMIC_PRODUCER`: already bound by E006j to the 10 steady producer families.
- **37** — `STARTUP_DIFFERS_FROM_STEADY`: common register address, but startup value differs and therefore cannot reuse the steady singleton.
- **184** — `STARTUP_ONLY`: address is absent from all four steady MAIN variants.

The partition sum is exactly **714**. There are no overlaps or uncovered startup register offsets.

81 startup register offsets vary across the four startup packets. This is phase/configuration variation, not evidence that every such register requires a continuously running algorithm.

## Startup-only owner closure

All 184 startup-only registers are source-locked to a Titan680 owner:

| Register family | Owner |
|---|---|
| 0x3F60..0x3F68 | `IFEBC101Titan680` |
| 0x4D60 | `IFEBayerGTM101Titan680` |
| 0x5260 | `IFEBayerLTM101Titan680` |
| 0x5460 | `IFELCAC111Titan680` |
| 0x6160 + 0x6168..0x61AC | `IFECST12Titan680` |
| 0x6360 | `IFEUVGamma101Titan680` |
| 0x9860..0x9884 + 0x9A60..0x9A84 | `IFEMNDS23Titan680` |
| 0x9C/9E/A4/A6/AC/AE ...60 and ...70..94 | `IFERoundClamp12Titan680` |
| 0x9C/9E/A4/A6/AC/AE ...68/6C | `IFECrop12Titan680` |
| 0xB060..0xB0A4 | `IFEAECBEStats17Titan680` |
| 0xB258/0xB25C | `IFEBHistStats16Titan680` |
| 0xB660..0xB6A4 | `IFETintlessBGStats17Titan680` |
| 0xB860..0xB8A4 | `IFEAWBBGStats17Titan680` |
| 0xBE60 + 0xBE68..0xBE70 | `IFERSStats14Titan680` |

The output-path windows are deliberately split at exact writer boundaries: RoundClamp owns each `...60` plus `...70..94`; Crop owns the interleaved `...68/6C` pair.

## 37 startup-vs-steady differences

All 37 also have explicit ownership:

- `0x008C` -> **VFE680 PERIOD_CFG**
- `0x3D78/0x3D80` -> PDPC
- `0x4570` -> WB
- `0x49D0..0x49E0` -> BPC_ABF
- `0xB26C` -> BHistStats16
- `0xBC60` and `0xBC6C..0xBCD0` -> BFStats25

### 0x008C correction

`0x008C` is **not an IQ producer register**. The accepted front VFE680 lineage defines it as `VFE680_X1E_PERIOD_CFG`.

The front corpus/materializer proofs establish that this field:
- is start/stream dependent;
- is caller-owned transport state;
- can change across Windows streams;
- must never be transplanted as a captured Windows constant.

Therefore rear startup must obtain `0x008C` from the Linux VFE/RT-CDM stream-state contract, not from an IQ callback or captured template.

## Consequence

Startup packet **structure** was closed by E006k. E006l now closes **register ownership/classification**:

- 468 fixed/common startup words can come from the safe steady singleton table;
- 25 existing dynamic words reuse E006j producer ownership;
- 37 startup-specific common words have named owners;
- 184 startup-only words have named Titan680 module owners;
- unresolved owners: **0**.

This does **not** mean every producer algorithm is implemented on Linux. It establishes who must supply each value and prevents accidental freezing of startup-phase or stream-local state.

Native rear Linux processed ISP remains **DENIED**.

## Next

Build an unreachable compile-only startup binding contract that combines:
1. reusable steady singleton provider;
2. E006j dynamic producer dispatch;
3. startup-specific module/transport providers from this map.

Then verify the combined startup+steady materializer compiles W=1 against the accepted CAMSS source before implementing missing producer algorithms or allowing any RT-CDM submission.
