# E003h Windows VFE1 dynamic-address oracle

Date: 2026-08-29

The exact same-machine Windows stack remains the behavioral oracle. This pass closes the VFE1 buffer-address writer and, critically, the first-address-set timing relative to BUS enable and ISP start completion. It supersedes the earlier working hypothesis that `qccamisp8380+0x27920` was the dynamic write-master address updater.

## Exact driver and raw evidence

Installed `qccamisp8380.sys` SHA-256:

`64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c`

Raw KD evidence copied byte-for-byte from SP7 into `windows-vfe1-dynamic-address/`:

- `E003H_VFE1_INITIAL_ADDRESS_ORDER_20260829.log`: 7,700 bytes, SHA-256 `3a2dd357e994f8f5d52668f7c914ad27a2dda6fdee8804e55daa3fcde1c5bed6`;
- `E003H_VFE1_ADDR_WRITER_20260829.log`: 18,160 bytes, SHA-256 `64e5a4e4f682829497f0868f00d2d0ff76b235f22d22c375184aaf37f2a788bc`;
- `E003H_VFE1_DYNAMIC_REQUEST_20260829.log`: 126,474 bytes, SHA-256 `ac68f99ad39bca7042c3f954eb3602040ba861cd0b0d276966d9f591f5305f5c`;
- `E003H_VFE1_LIVE_CORRELATE_20260829.log`: 16,344 bytes, SHA-256 `102761bf27d562dc863843f79fc6e5f87b4be27140becfc5cc250f613c2b04ae`.

`extract_vfe1_dynamic_address.py` is fail-closed to those hashes and the exact installed driver. Extractor SHA-256 is `e8d9e278de52f1e1d363c60621a2cc789dc33f149cb53d222bab0b0092419211`; derived `vfe1-dynamic-address-oracle.json` SHA-256 is `925028750e8be60c65a69f24349bb540b0ba0776726f40d59273b0be7f464282`.

## Exact Windows writer

The dynamic address writer is the indirect-callback function beginning at `qccamisp8380` RVA `0x1dd20`, not RVA `0x27920`.

The exact installed driver contains:

- RVA `0x1dea4`: load the VFE client image-address register offset from object field `+0x3408`;
- RVA `0x1deac`: store the computed image/data IOVA;
- RVA `0x1dee8`: load the metadata-address register offset from object field `+0x3450`;
- RVA `0x1def4`: store the computed metadata IOVA for metadata-bearing clients.

The same live object proves `+0x3408 = 0x04` and `+0x3450 = 0x40`. Therefore the Windows dynamic writer targets per-client `IMAGE_ADDR +0x04` and, for FULL Y/C, `META_ADDR +0x40`.

Live breakpoints at the write site reproduce the physical VFE1 MMIO values exactly. The address sequence is:

1. FULL Y, resource `0x3000`, selector 0;
2. FULL C, resource `0x3000`, selector 1;
3. DS4 `0x3001`;
4. DS16 `0x3002`;
5. AEC_BE `0x301c`;
6. RS `0x3010`;
7. BHIST `0x300f`;
8. AWB_BG `0x300e`;
9. TL_BG `0x300c`.

Only FULL Y/C are metadata-bearing on this accepted path.

## Initial and per-frame lifecycle

A dedicated second oracle boot captured BUS configuration, BUS enable/disable, the dynamic writer and `ISP_START_DONE` in one ordered log. The first complete session is unambiguous:

`BUS static config -> BUS enable -> initial dynamic IOVA set -> ISP_START_DONE -> repeated per-frame dynamic IOVA sets -> BUS disable`

Static configuration order is:

`FULL[0] -> FULL[1] -> DS4 -> DS16 -> AEC_BE -> RS -> BHIST -> AWB_BG -> TL_BG`

Resource enable and disable order is:

`FULL -> DS4 -> DS16 -> AEC_BE -> RS -> BHIST -> AWB_BG -> TL_BG`

Offline disassembly of the exact `0x1d830` enable/disable function additionally closes the internal FULL order: WM0 is toggled first, then WM1. The same function is used for enable and disable.

The first nine IOVA writes occur **after all BUS resources are enabled and before `ISP_START_DONE`**. The next complete nine-client IOVA set occurs after `ISP_START_DONE`, establishing the repeated per-frame/request update layer.

## QC10C relationship and allocation lifetime

The writer independently reconfirms the already-accepted one-allocation QC10C layout. Taking FULL Y metadata as allocation base:

- Y metadata: `base + 0`;
- Y TP10 data: `base + 0x6000`;
- C metadata: `base + 0x4f2000`;
- C TP10 data: `base + 0x4f5000`;
- V4L2 `sizeimage`: `0x76b000`.

Successive Windows QC10C slots advance by `0x76c000`, i.e. the Windows allocator rounds the accepted surface to a 16-KiB slot. The auxiliary buffers show the same allocator behavior: their observed slot stride is `ALIGN(frame_incr, 0x4000)`. This is an **allocator observation**, not a hardware requirement and not a Linux ABI. Linux must program the actual DMA IOVA of each queued allocation and must not reproduce or hard-code the Windows ring.

## Why `0x27920` is rejected as the address writer

Seven complete `0x27920` request buffers were captured around ISP start. Post-start payloads repeat byte-for-byte while live VFE1 `IMAGE_ADDR`/`META_ADDR` values continue changing. The direct `0x1dd20` writer, by contrast, produces values that exactly match the live MMIO snapshots. `0x27920` remains part of request/config processing but is no longer an address-update target.

## Linux consequence

The BUS lifecycle/address model is now closed enough to compile a Linux representation without freezing Windows state:

- static client state is session-scoped;
- resource enable precedes the initial dynamic address set;
- FULL uses WM0 then WM1 internally;
- every initial/per-frame image/meta address comes from the current backing allocation;
- DS4/DS16/statistics require their own dynamic allocations;
- Windows allocator slot strides are never Linux constants.

This oracle does **not** authorize VFE1 PIX streaming. Linux PIX remains blocked until the BUS recipe, RT-CDM/IQ path and completion/buffer ownership are integrated and statically proven together.
