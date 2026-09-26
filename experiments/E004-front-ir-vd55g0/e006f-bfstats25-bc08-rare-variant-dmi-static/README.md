# E006f — BFStats25 BC08 producer and rare-variant DMI closure

Parent Git: `e8872642` (E006e A98 cross-variant result).

Status: **STATIC PASS**. No Linux camera runtime and no new Windows oracle run were performed.

## Question

E006e captured A98 but a healthy 90-second rear 4K run still did not encounter steady 8F0 or steady 658. Rather than consume another physical experiment merely to copy those rare payload bytes, E006f asks whether the missing variants introduce any DMI producer or payload identity that is not already understood.

## Exact Windows producer

Exact same-SP11 binary:

- `QcDeviceMFT8380.dll`
- SHA-256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`

The existing analyzed Ghidra DeviceMFT database directly resolves the BC08 command builder.

### Titan680 CreateCmdList

RVA `0xB4F4E0` decompiles with surviving source strings as:

`CamX::IFEBFStats25Titan680::CreateCmdList`

from:

`camx/src/hwl/isphwsetting/titan680/camxifebfstats25titan680.cpp`

It writes:

- `WriteDMI(..., 0xBC08, selector 1, ..., payload_bytes = ROI_count * 12)`
- when gamma LUT is enabled/valid, `WriteDMI(..., 0xBC08, selector 2, ..., payload_bytes = 0x80)`

The exact error strings identify these respectively as:

- **BF ROI DMI buffer**
- **BF gamma LUT DMI buffer**

The E006a steady payload sizes are 300 and 128 bytes. The selector-1 size is therefore exactly 25 x 12-byte ROI records for those observed steady packets; selector 2 is the fixed 128-byte gamma LUT.

### Titan680 LUT/register packing

RVA `0xB4FC20` is source-identified as:

`CamX::IFEBFStats25Titan680::PopulateLUTConfig`

It consumes the current BF stats request settings, programs the BF register block beginning at `0xBC58`, and selects the current DMI bank from the per-request BF state.

### Request-time BFStats25 producer

RVA `0xA1D340` contains the source-identified BFStats25 request logic from:

`camx/src/hwl/ispiqmodule/camxifebfstats25.cpp`

Surviving strings and decompilation source-lock:

- incoming **AF config pointer** validation;
- `pAFConfig->BFStats.BFStatsROIConfig.numBFStatsROIDimension`;
- `pAFConfig->BFStats.BFGammaLUTConfig.numGammaLUT`;
- `pAFConfig->BFStats.BFGammaLUTConfig.isValid`;
- ROI validation/adjustment/sorting;
- `UpdateROIDMITable`;
- `GammaGetHighLowBits`;
- independent ROI/gamma DMI bank state.

The request logic clears its per-request change flags, derives current ROI/gamma configuration from the incoming AF config, and only sends a new hardware-setting update when **ROI changed, gamma changed, or force-update** is true. The current ROI/gamma LUT bank is then published into the request context.

This gives a direct code explanation for E006b/E006c/E006e evidence:

- BC08 may vary during startup while AF statistics configuration is being established;
- after AF BF configuration stabilizes, the same ROI/gamma payloads can persist across different RT-CDM MAIN command shapes;
- BC08 is not an independent image-IQ tuning corpus that must be captured separately for every MAIN variant.

## Rare steady variants introduce no new DMI identity

E006a's exact decoded steady DMI sets are:

### MAIN 0x8F0

- LSC411 `0x4308` selectors 1/2/3
- GTM131 `0x5A08` selector 1
- `0x5F08` selectors 1/2/3
- `0xA008` selectors 1/2
- `0xA208` selectors 1/2
- BFStats25 `0xBC08` selectors 1/2

### MAIN 0x658

- GTM131 `0x5A08` selector 1
- BFStats25 `0xBC08` selectors 1/2

Therefore neither rare variant introduces a new DMI family.

Their DMI values fall entirely into already-closed classes:

1. **LSC/Tintless request producer**
   - `0x4308` selectors 1/2
   - selector 3 is cross-variant-stable in AC8 and A98
2. **GTM/TMC request producer**
   - `0x5A08` selector 1
3. **Cross-variant-stable payload identities**
   - `0x5F08`, `0xA008`, `0xA208` (and other E006e-confirmed stable families where present)
4. **BFStats25 AF-request producer**
   - `0xBC08` selector 1 = current ROI table
   - `0xBC08` selector 2 = current BF gamma LUT

## Decision

Do **not** spend another Windows experiment merely to obtain 8F0/steady-658 DMI payload bytes.

A correct Linux rear materializer must generate/request-bind the dynamic producer outputs rather than freeze a Windows snapshot:

- current LSC/Tintless payloads;
- current GTM/TMC payload;
- current BFStats25 ROI/gamma payloads.

The fixed/cross-variant-stable identities may be materialized from independently derived producer/template data already established in the project, subject to normal clean-room rules.

If future runtime evidence contradicts this producer model, reopen the gate with a fresh experiment identity. No existing consumed E006 identity may be replayed.

## Remaining work

This closes the **missing rare-variant DMI ownership** question, not native rear runtime authorization.

Next engineering step:

- build an **unreachable/unloaded rear materializer skeleton** from the E006a command structures;
- bind dynamic slots to the accepted LSC/Tintless, GTM/TMC and BFStats25 producer interfaces;
- reuse independently derived stable payload producers/templates;
- verify parser/materializer invariants and compile with `W=1`;
- only then design a guarded Linux runtime candidate.

Native rear Linux processed ISP remains **DENIED**.
