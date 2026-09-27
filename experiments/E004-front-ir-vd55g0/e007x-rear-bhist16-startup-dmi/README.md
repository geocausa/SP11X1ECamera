# E007x — rear BHistStats16 startup DMI priming

Parent Git: `8be45054` (E007w PERIOD_CFG semantic provider PASS).

Status: **COMPILE-ONLY PASS**.

## Why this checkpoint exists

The first full startup-request assembly audit found two packet-0 DMI identities that were absent from the earlier steady-focused first-frame blocker audit:

- `0xB208`, selector 1, 4096 bytes;
- `0xB208`, selector 2, 80 bytes.

Ownership was already source-locked to `IFEBHistStats16Titan680` by E006k/E006u, but the payload producer had not been made explicit.

## Surface source lock

Pinned Surface `IFEBHistStats16Titan680::CreateCmdList` at `0x180b3fc90` performs the startup path only when the startup flag is set.

It:

1. advances to the request-owned BHist DMI region;
2. zeroes exactly `0x1050` bytes;
3. writes selector 1 from offset 0 for `0x1000` bytes;
4. writes selector 2 from offset `0x1000` for `0x50` bytes.

Therefore both startup DMI payloads are semantic **zero priming**, not captured LUT state.

The retained rear E006b oracle independently reports both payloads as all-zero and their hashes equal clean zero buffers of those sizes.

## Provider

`e007x_bhist16_startup_dmi()`:

- accepts only startup packet 0;
- accepts only DMI register `0xB208`;
- accepts selectors 1/2 with exact lengths;
- generates the payload with `memset(..., 0, bytes)`;
- fails closed otherwise.

No captured payload bytes are embedded.

## Audit correction

E007r/E007w's earlier first-frame blocker count was based on the steady/stable DMI catalog plus known dynamic families. The full startup topology contains this additional BHist priming pair.

E007x closes that omission. After E007x, the full **startup DMI union of 18 identities** has a clean producer boundary.

## Next gate

Compose all four rear startup MAIN command lists offline from the E006k symbolic topology, E007d/E007w register providers and the complete DMI provider set. Compare structurally against the private E006a Windows oracle with only relocation/address fields normalized.

No submission is authorized by this checkpoint.

## Build result — PASS

The full accepted E006/E007 provider chain through E007x compiled in an isolated CAMSS source copy.

- W=1 warnings/errors: 0;
- qcom-camss.ko: 13,850,016 bytes;
- SHA-256: `5dc6b5313174e16aa03bbc516011a0ff67265af1ba7ed61113e810e697c35fbb`;
- vermagic: exact Golden `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`;
- retained symbols: `e007x_bhist16_startup_dmi`, `e007x_bhist16_startup_dmi_recipe`;
- install/load/camera/DMI/RT-CDM submission: none.
