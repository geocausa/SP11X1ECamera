# E003h Windows IFE patch/DMI oracle

Same-machine Windows on this exact SP11 is the behavioral oracle. This checkpoint closes the byte-level DMI/LUT input of the four initial IFE `0x803` packets; it does **not** infer undocumented IQ-block names from payload shape.

## Canonical final capture

- raw: `raw/E003H_IFE_PATCH_DMI_EXACT_20260828.log`
- bytes: `5,832,792`
- SHA-256: `719043805efd57d26483497c0c1964251e77461ccdb7213e5fdc1947defbffc7`
- exact installed `qccamisp8380.sys` SHA-256: `64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c`
- four standalone DEVICE_START IFE `0x803` hits
- front WinRT reader: `StartAsync=Success`, normal Stop
- Golden restored afterward with protected kernel/initrd/DTB hashes unchanged and empty `next_entry`

## Windows patch mechanics

Exact ARM64 disassembly of the installed KMD mechanically gives the packet fields and patch path. The packet payload base is `packet+0x74`; `patchsetOffset` is at `+0x28`, `numPatches` at `+0x2c`. Each patch record is 24 bytes:

`u64 dst_handle | u32 dst_offset | u64 src_handle (packed at +0x0c) | u32 src_offset`

Windows reads `[src_handle+0]` as the source IOVA base and `[src_handle+8]` as the source CPU VA, writes low32(`source_iova + src_offset`) to `destination_cpu + dst_offset`, and uses `source_cpu + src_offset` as the DMI virtual address. The four patch counts are `18/16/11/1`, exactly matching the four main-CDM DMI counts.

## Closure

- **46/46** patch records correspond one-for-one with the **46/46** decoded DMI commands.
- Every destination offset equals the command-buffer slot base plus the exact DMI address-word offset (`stream_offset + 4`).
- Every patched DMI IOVA equals the captured source-I/O base plus that patch record's source offset.
- Qualcomm public CDM code at pinned commit `0f16924ff6a7f9bb56a7e958016da2ed8a174f2f` is used only to confirm the encoded DMI length field means **payload bytes = length + 1**.
- All required bytes are inside the captured `0x20000` source window; maximum referenced end is exactly `+0x1bccc`.
- The source window was byte-identical at all four hits; SHA-256 `bbb9dc35ec2fccc68c81af7f2e13813c75d3c27d5b4450903f5004dc3cc69d9a`.
- 46 references form **21 exact `(register, selector, length, SHA)` groups** and deduplicate to **16 unique payload byte strings**.

## Exact DMI identities

| DMI register | Selector | Bytes | Payload SHA-256 | References |
| --- | ---: | ---: | --- | --- |
| `0x3d08` | 1 | 512 | `076a27c79e5ace2a3d47f9dd2e83e4ff6ea8872b3c2218f66c92b89b55f36560` | P0/D0@0x0, P1/D0@0x8000, P2/D0@0x10000 |
| `0x4308` | 1 | 884 | `6447e93bf908c694541ea71ba99613e6618696ffbbe3e3d41b5660e65ed7d1d8` | P0/D1@0x400 |
| `0x4308` | 1 | 884 | `96a65dc04c64a3f483010e100a0f9069fc0a08368c12d1d94eabe44149db39d5` | P1/D1@0x8400, P2/D1@0x10400 |
| `0x4308` | 2 | 884 | `6b40f8ca05febaa4967a85161c4488adeaa68526af3db023cf82b329732f43bd` | P1/D2@0x8774, P2/D2@0x10774 |
| `0x4308` | 2 | 884 | `d61327d1fde5a597ac5ea9d70fe9e1e0ab24831482c2172cb1b7b3d0ae3908e5` | P0/D2@0x774 |
| `0x4308` | 3 | 884 | `6ca83adefc47fc9ab71637c150b95b33083e61e507dff2ee5f2692aa27e1453e` | P0/D3@0xae8, P1/D3@0x8ae8, P2/D3@0x10ae8 |
| `0x4708` | 1 | 512 | `2f5dcd1256b95729a2c7ed1fef920c707b03ff17f65b268d19eea8b345392881` | P0/D4@0x62e |
| `0x4708` | 1 | 512 | `c19141e4374c3e85cbe58105f1689f930ae240ad6aebb6c57f42b764c06406c3` | P1/D4@0x862e, P2/D4@0x1062e |
| `0x4908` | 1 | 256 | `c48a9ca4c0431ee4d98b78f9c59858a53adacd5604c88bd0c7f591ff2858e6ed` | P0/D5@0x1ab8, P1/D5@0x9ab8, P2/D5@0x11ab8 |
| `0x5408` | 1 | 68 | `1751ac12e70e15b4f76c16775cd329ae55973b612521dab2de828a5cdb6c8ab3` | P0/D6@0xcef, P1/D6@0x8cef |
| `0x5408` | 2 | 68 | `1751ac12e70e15b4f76c16775cd329ae55973b612521dab2de828a5cdb6c8ab3` | P0/D7@0xd33, P1/D7@0x8d33 |
| `0x5a08` | 1 | 2048 | `b71d4b3eadec95941586227f171e771ae5dc1c70fd48fa5ebf599dcf8fd77d81` | P0/D8@0x34cc, P1/D8@0xb4cc, P2/D6@0x134cc, P3/D0@0x1b4cc |
| `0x5f08` | 1 | 1024 | `5a0237322ad86a63afa00152f43d049ba9db6494753a20fbf35149a51e978f2b` | P0/D9@0x3ccc, P1/D9@0xbccc |
| `0x5f08` | 2 | 1024 | `5a0237322ad86a63afa00152f43d049ba9db6494753a20fbf35149a51e978f2b` | P0/D10@0x40cc, P1/D10@0xc0cc |
| `0x5f08` | 3 | 1024 | `5a0237322ad86a63afa00152f43d049ba9db6494753a20fbf35149a51e978f2b` | P0/D11@0x44cc, P1/D11@0xc4cc |
| `0xa008` | 1 | 768 | `2c67e29e973aaaa45ac5aa18b64dbd08745be2096ffbc0d618dfff0adadffd2b` | P0/D12@0x4acc, P1/D12@0xcacc, P2/D7@0x14acc |
| `0xa008` | 2 | 768 | `2c67e29e973aaaa45ac5aa18b64dbd08745be2096ffbc0d618dfff0adadffd2b` | P0/D13@0x4dcc, P1/D13@0xcdcc, P2/D8@0x14dcc |
| `0xa208` | 1 | 384 | `8c9b8daa8246b2cdcf7b999509c388b4fc95555f37ce9c8eff04995f172ea9af` | P0/D14@0x50cc, P1/D14@0xd0cc, P2/D9@0x150cc |
| `0xa208` | 2 | 384 | `8c9b8daa8246b2cdcf7b999509c388b4fc95555f37ce9c8eff04995f172ea9af` | P0/D15@0x524c, P1/D15@0xd24c, P2/D10@0x1524c |
| `0xb208` | 1 | 4096 | `ad7facb2586fc6e966c004d7d1d16b024f5805ff7cb47c7a85dabd8b48892ca7` | P0/D16@0x5ccc |
| `0xb208` | 2 | 80 | `5b6fb58e61fa475939767d68a446f97f1bff02c0e5935a3ea8bb51e6515783d8` | P0/D17@0x6ccc |

## Naming boundary

The pinned public Qualcomm VFE680 kernel header exposes top/bus register layout but does not publish the pixel-IQ DMI block register map for these offsets. Therefore this checkpoint intentionally preserves the exact hardware identities as register offset + selector + byte payload rather than guessing names such as gamma, rolloff, GTM or LTM from table size. Semantic block naming must be proven separately from an authoritative layout or the exact Windows binary.

## Supporting captures

- `raw/E003H_IFE_CDM_COMPANION_EXACT_20260828.log` (136,290 bytes, SHA-256 `3d9d1beb74641c8e699f045abcc79384c52d5365780dd3134a99ab0dbd42e194`) proved descriptor 1 is CSID1 IPP command data and reproduced the Windows 3840x2160 crop state.
- `raw/E003H_IFE_CDM_DMI_FULL_EXACT_20260828.log` (1,762,896 bytes, SHA-256 `7555716caa88769aedfbf478c80bd1ff9d14d3fb2512ac368b7f2fb9cb4a17b2`) proved descriptor 2 is not the DMI source allocation; its IOVA is 1 MiB above the DMI source and the full captured slice contains no matching camera-range IOVA entries.

## Generated artifacts

- `extract_patch_dmi_oracle.py`: fail-closed parser/correlator.
- `patch-dmi-summary.json`: machine-readable patch/DMI proof and 21 identity groups.
- `dmi-payloads.csv`: all 46 references.
- `dmi-source-window.bin`: exact 128 KiB source window used by the four packets.
- `dmi-payloads/*.bin`: 16 SHA-named unique payload byte strings.

## Next static task

Combine these exact DMI identities with the already-decoded 2,131 main-CDM register writes. Classify writable pixel-IQ/scaler/statistics configuration versus dynamic addresses/status, prove the required VFE1 MMIO aperture from the exact access set, then derive a fail-closed Linux VFE1 PIX/TP10-UBWC architecture. No runtime/front frame is authorized by this oracle alone.
