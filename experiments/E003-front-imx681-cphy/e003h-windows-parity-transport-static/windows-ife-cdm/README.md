# E003h Windows IFE initial-CDM oracle

Same-machine Windows on this exact SP11 remains the behavioral oracle. Qualcomm's public camera-driver source at commit `0f16924ff6a7f9bb56a7e958016da2ed8a174f2f` is used only to decode the standard CDM command encoding and names.

## Exact capture

The accepted raw evidence is `raw/E003H_IFE_CDM_INIT_EXACT_20260828.log`:

- bytes: `175222`
- SHA-256: `a22f94b6a024226791c139336b17777f1359f1847146bafa6e092215e86e762a`
- source: SP7 KDNET while the exact same-machine Windows `Surface Camera Front` WinRT reader executed one normal StartAsync/StopAsync cycle
- qccamisp8380.sys SHA-256: `64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c`
- capture point: the four initial IFE `0x803` submissions inside DEVICE_START, after IFE start and before CSID start

The broad exploratory CDM capture is intentionally not canonical. This directory preserves the bounded four-packet startup capture only.

## Decoder

`extract_initial_ife_cdm.py` parses the KD descriptor records, extracts descriptor 0's mapped CPU bytes to the descriptor's exact used length, and decodes standard Qualcomm CDM commands fail-closed. It accepts REG_CONT, REG_RANDOM, DMI, BUFFER_INDIRECT, GEN_IRQ, WAIT_EVENT, CHANGE_BASE, PERF_CONTROL, DMI32/64, COMP_WAIT, CLEAR_COMP_WAIT and WAIT_PREFETCH_DISABLE; any unknown opcode or length mismatch is fatal.

All four main command streams decode exactly to their declared lengths with zero unknown opcodes:

| Packet | Used bytes | CDM commands | Register writes | DMI commands | Writes >= +0x4000 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 3732 | 110 | 695 | 18 | 660 |
| 1 | 3636 | 103 | 687 | 16 | 655 |
| 2 | 2308 | 52 | 462 | 11 | 430 |
| 3 | 1256 | 13 | 287 | 1 | 270 |

The decoded main streams contain no CHANGE_BASE commands. Packet 3 independently writes `+0x24=0x00006000` and `+0x90=0x00000001`; both values match the separate E003g same-machine Windows-live VFE1 MMIO oracle. This mechanically pins the active CDM register base to VFE1 at `0x0ac71000`.

The maximum decoded register offset is `+0xbe70`. Across the four startup packets, 2015 register writes fall outside `+0x0000..+0x3fff`. Therefore Linux's current upstream X1E VFE1 `0x4000` MMIO aperture is insufficient to represent the observed Windows PIX/ISP startup path. The older Denali-derived `0xf000` VFE aperture is now a live hypothesis worth re-evaluating, but this oracle does not by itself authorize changing the Linux resource size.

## Generated artifacts

- `initial-ife-cdm-summary.json`: deterministic machine-readable provenance, descriptors, decoded counts and DMI command metadata.
- `packetN-main-cdm.bin`: exact descriptor-0 command bytes up to each used length.
- `packetN-register-writes.csv`: flattened register writes decoded from each main stream.

Re-running the parser into a fresh directory reproduces all nine derived files byte-for-byte.

## Remaining oracle

The main stream contains 46 DMI commands total, and those commands reference LUT/data IOVAs. Each Windows startup packet also carries descriptor 1 (type `0x12`) and descriptor 2 (type `0x0c`). Their mapped bytes were not preserved in this capture. Full ISP parity therefore remains blocked until a bounded same-machine Windows follow-up captures the companion descriptor mappings/used bytes and mechanically resolves the DMI/LUT payloads. Do not synthesize LUT contents or RAW-to-YUV/scaler state from the main stream alone.
