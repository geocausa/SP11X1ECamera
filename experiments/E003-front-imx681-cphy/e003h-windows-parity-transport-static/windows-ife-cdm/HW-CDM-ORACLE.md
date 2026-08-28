# E003h same-machine Windows hardware-CDM oracle

This oracle closes the DMI execution architecture for the accepted native Windows front-camera path. Windows remains the behavioral authority; the public Qualcomm camera-driver tree is used only to name the RT-CDM v2.1 register layout.

## Evidence

- raw KD log: `raw/E003H_HWCDM_ORACLE_20260828.log`
- bytes: `27014`
- SHA-256: `458b05c41718c7d01d0efb2921d1f6e2e4323e94e24447e379499544ca21cc1a`
- exact `qccamisp8380.sys` SHA-256: `64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c`
- native WinRT front reader reached `StartAsync=Success` and later completed normal `StopAsync`/dispose.
- after Windows, the machine returned to Golden Linux; protected kernel/initrd/DTB hashes matched, `saved_entry` remained `sp11-audio-fullio-v19c`, and `next_entry` was empty.

`extract_hwcdm_oracle.py` is fail-closed against the exact raw hash and regenerates `hwcdm-oracle-summary.json`.

## Native acquire chooses hardware CDM

Static disassembly of the exact Windows KMD first pins the decision path:

- command `0x802` copies input-resource byte `+0x90` into internal byte `+0x511` (`RVA 0x16780` / `0x16788`);
- the KMD diagnostic formatter names input-resource `+0x90` **`SW CDM`**;
- later `+0x511` is read at `RVA 0x1827c`;
- zero enters the **`Enabling hw cdm`** path at `RVA 0x183d8` and sets internal hardware-CDM flag `+0x830=1`;
- nonzero enters **`Enabling sw cdm`** at `RVA 0x1881c` and clears `+0x830`;
- the exact software-CDM parser recognizes DMI opcodes but explicitly skips DMI/LUT programming.

The live same-machine breakpoint result is decisive:

- `SWCDM_BYTE=00` at the acquire-copy point;
- hardware-CDM branch hit;
- software-CDM branch did **not** hit.

Therefore the native front path does not rely on the Windows software CDM fallback for its DMI/LUT programming.

## Exact RT-CDM resources

The exact KMD resource parser recognizes literal resources `RT_CDM_0` and `RT_CDM_1`. On this boot its mapped pointer array held:

| resource | mapped Windows VA | KD PTE PFN | physical base |
|---|---:|---:|---:|
| RT_CDM_0 | `0xffff988134a3b000` | `0xac25` | `0x0ac25000` |
| RT_CDM_1 | `0xffff988134a3c000` | `0xac26` | `0x0ac26000` |

Both live engines report hardware version `0x20010000`, matching Qualcomm's public `qcom,cam-rt-cdm2_1` / CDM v2.1 layout.

## Which engine executes the front path

During the native front stream:

### RT_CDM_0 (`0x0ac25000`)

- `HW_VERSION +0x000 = 0x20010000`
- `CORE_CFG +0x018 = 0x0002011f`
- `CORE_EN +0x01c = 1`
- `FE_CFG +0x020 = 0x07ff000f`
- FIFO0 base/length `+0x050/+0x054 = 0/0`
- current BL base/length `+0x0e8/+0x0ec = 0/0`

### RT_CDM_1 (`0x0ac26000`)

- `HW_VERSION +0x000 = 0x20010000`
- `CORE_CFG +0x018 = 0x0000011f`
- `CORE_EN +0x01c = 1`
- `FE_CFG +0x020 = 0x07ff000f`
- FIFO0 base `+0x050 = 0x17b82714`
- FIFO0 length `+0x054 = 0x00100013`
- FIFO0 store `+0x058 = 0`
- FIFO0 cfg `+0x05c = 0x01000000`
- current BL base `+0x0e8 = 0x17b82714`
- current BL length `+0x0ec = 0x00100013`
- current-used-AHB-base `+0x0f0 = 0x00057000`
- debug status `+0x0f4 = 0x0062b904`
- FIFO1/2/3 base and length fields are all zero in the extended live dump.

That makes **RT_CDM_1 the mechanically proven hardware CDM engine for the native front-camera path**. The captured base/length values are dynamic command-buffer state and must not be hard-coded into Linux.

After normal Windows StopAsync, the first `0x100` bytes of both RT-CDM mappings read uniformly as the powered-off sentinel `0x80000000`.

## Linux consequence

This closes the previous selector-mechanism ambiguity:

1. the Windows main IFE CDM stream contains DMI commands whose selector is part of the CDM opcode;
2. the exact native front acquire requests `SW CDM = 0`;
3. Windows takes its hardware-CDM path;
4. RT_CDM_1 at `0x0ac26000` is the active v2.1 engine;
5. the older direct VFE DMI read/replay recipe was already rejected by the bounded same-machine diagnostic.

So **direct CPU writes to guessed VFE680 DMI selector/data ports are not an acceptable parity implementation**. The minimum Linux architecture must execute the exact Windows-proven command semantics through RT-CDM1 (or an alternative only if it is separately proven bit-for-bit equivalent at the hardware interface).

No Linux camera runtime is authorized by this result alone. RT-CDM1 clock/power/reset ownership, IOMMU/DMA addressability, IRQ/completion handling, safe shutdown, and integration with the VFE1 PIX/FULL path must be closed statically before a live Linux submission.
