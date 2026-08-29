# E003h Windows VFE1 Epoch0 RT-CDM batches

Date: 2026-08-29

## Result

The steady-state Windows IFE Epoch0 RT-CDM batch format is now mechanically closed at the command-byte level for this same-machine front stream.

Canonical clean capture:

- `windows-vfe1-epoch0-cdm-batches/E003H_VFE1_EPOCH0_CDM_BATCHES_CLEAN_20260829.log`
- bytes: `3,994,804`
- SHA-256: `1e8dc9671296e35a0704315588669fc8ed97612fd4b72c1d71b11bb7244d9a7f`
- exact installed `qccamisp8380.sys`: 376,560 bytes, SHA-256 `64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c`

The deterministic extractor `extract_vfe1_epoch0_cdm_batches.py` is SHA-256 `d02f7faaeb034e0d7b0931f6c1490a37211784cf535599b29544baf8f3fc329a`. Derived fail-closed oracle `vfe1-epoch0-cdm-batches-oracle.json` is SHA-256 `3bcf4efe34c891dcc6bc78c3cefc94d916ffd71e27dab81e75493f9ed320dce4`.

## Exact queue-record contract

Exact driver disassembly pins Epoch0's selector-2 consumer and the 40-byte BL queue record. At RVA `0x287d8` Windows copies the first 32 bytes of one record, then at `0x287dc` copies the final 8 bytes. The live probe independently resolves the stack copy as:

- `+0x20`: hardware BL IOVA;
- `+0x28`: mapped CPU alias of the BL bytes;
- `+0x30`: encoded length;
- encoded length is **byte_count - 1**, not dword-count minus one.

The same selector-2 path writes FIFO0 base/encoded-length/store at RVAs `0x28884`, `0x2888c`, `0x28894`.

This matters because the CPU alias allowed exact command bytes to be captured without inferring Windows allocation geometry.

## Capture census

The clean log contains exactly **179 complete batches / 894 BL records**. The first four batches reproduce the previously proven startup main lengths `0xe94`, `0xe34`, `0x904`, `0x4e8`. The following **175** are steady-state Epoch0 batches.

Every steady batch contains exactly five BL records:

1. 4-byte `CHANGE_BASE 0x0000f000`;
2. one variable-size main IFE command list;
3. 4-byte `CHANGE_BASE 0x00057000`;
4. fixed 0x10-byte two-register list;
5. fixed 0x14-byte register + `GEN_IRQ` list.

BL0, BL2 and BL3 are byte-identical across all 175 steady batches. BL4 differs only in its final GEN_IRQ userdata dword; that userdata equals the observed batch number for every steady sample.

## Five real main-BL variants

Windows does not use one universal per-frame main command list. The 175 steady samples split into five exact structural variants:

| Main bytes | Samples | CDM commands | Register writes | DMI commands | Per-frame register-value fields |
| ---: | ---: | ---: | ---: | ---: | ---: |
| `0x958` | 8 | 56 | 472 | 14 | 24 |
| `0x868` | 42 | 45 | 436 | 12 | 20 |
| `0x83c` | 46 | 43 | 429 | 12 | 14 |
| `0x6b8` | 24 | 35 | 352 | 8 | 10 |
| `0x5a4` | 55 | 22 | 315 | 2 | 6 |

Within each variant, the command topology is identical across all samples. Every byte-level variation is mechanically classified as either a DMI address word or a register-value word. There are no unexplained varying command bytes.

After zeroing all DMI address fields plus only the observed per-frame register-value fields, every sample of a variant becomes byte-identical. Normalized SHA-256 values are:

- `0x958`: `6c979a87c9a550ba1dfbfe740e714f8538238e7537251f855ba997c1fadc42a2`;
- `0x868`: `001b086bcc594a37a3a8b846a038f8e534a3b7974eb87a03a2961f1247deb856`;
- `0x83c`: `3bcc4def6731cd107ad70ffa7d0c5c52e7a712ef6436814e50a7b9725aaf9c61`;
- `0x6b8`: `ed90abec133e939674d19bfcbcc2250fee9e23cb539306fbeb574054b43df6d8`;
- `0x5a4`: `3dd3c9d87f07db98df529ff522a9541cf0c9c38f0d5862c425431660b467f0e9`.

The full per-variant DMI field positions, selectors/sizes and dynamic register field positions are in the JSON oracle.

## Correction to 0023

The earlier 0023 ownership gate correctly established the scheduler order and correctly rejected inventing a Linux direct-MMIO polling/rewrite loop. Its narrower statement that no post-start software write had been proven for `+0x008c/+0x3b70/+0x3d78..+0x3d84` is now superseded.

The clean Epoch0 command capture proves Windows **does carry those register identities in queued steady-state RT-CDM command lists**. In particular, every observed steady main variant includes the tail writes:

- VFE1 `+0x24 = 0x00006000`;
- VFE1 `period_cfg +0x8c = 0x37213000`;
- VFE1 `+0x90 = 1`.

The important ownership distinction is therefore:

- these values are part of the queued per-frame RT-CDM program;
- they are **not** evidence for a separate CPU/direct-MMIO periodic rewrite loop;
- live readback mutation by hardware must not be confused with the source of the next command-list values.

## Remaining gap

The command-list topology and command bytes are closed, but the per-frame **DMI payload bytes are not**. The DMI command words expose per-batch IOVAs, but the simple main-BL IOVA-to-CPU-alias delta does not map the DMI source allocation; the predicted addresses read zero. Therefore DMI payload bytes must be recovered from their actual Windows source handles/CPU aliases rather than guessed.

The five main-BL variant-selection rule is also not yet named. Do not infer semantic names from list size or occurrence pattern.

No Linux runtime is authorized by this oracle.
