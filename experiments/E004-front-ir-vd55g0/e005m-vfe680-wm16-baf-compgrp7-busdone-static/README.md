# E005m — VFE680 WM16 STATS_BAF comp-group-7 hardware buffer-done contract

**2026-09-25; parent E005l Git `8747f7780fbf056dcf891e202e3e3345eb98d50d`.** Read-only source convergence only. No camera stream, reboot, module load, MMIO write, IRQ enable/ack change, DMA allocation, KD session, proprietary payload export or Golden mutation occurred.

## Why this experiment exists

The current rear-native-ISP blocker is narrower than the older generic "find BF IRQ" wording. Same-SP11 Windows evidence already source-locks BF event `0x0f`, resource `0x300d`, independent software FIFO group 8 and a WM16 status callback. Physical Windows snapshots also show VFE1 WM16 enabled. E005l further shows user-mode STAT metadata can expose aggregate key/tag, but none of those facts alone prove that the exact WM16 hardware buffer associated with a BF queue entry completed DMA and is safe to retire.

The accepted SP11 Linux VFE680 implementation still has a no-op ISR:

`camss-vfe-680.c::vfe_isr() -> IRQ_HANDLED`

so it does not currently provide an independent native WM16 completion witness.

This experiment pins Qualcomm's public camera-driver VFE680 implementation at commit
`82ac3a671a5b0a4e3b3ac4519208af1d37a93eb6` / tag `v1.0.6` and compares its exact VFE680 BUS model against the accepted SP11 CAMSS and the already-pinned Windows facts.

## Exact independent VFE680 contract

Qualcomm's VFE680 hardware description independently establishes all of the following:

| VFE680 fact | Exact source value | Relevance |
| --- | --- | --- |
| Write master 16 | `wm_id = 16`, description `STATS_BAF` | Independently matches the Windows BF/WM16 association. |
| WM16 config | base + `0x1e00` | Matches the Windows callback's WM16 CFG0 access. |
| WM16 consumed-address status | base + `0x1e70` | Matches the Windows callback's WM16 ADDR_STATUS0 access. |
| WM16 composite group | `CAM_VFE_BUS_VER3_COMP_GRP_7` | Defines which hardware completion bit owns the BAF output. |
| Composite-group-7 done mask | BUS IRQ status0 `BIT(7)` | Gives a source-defined hardware completion predicate distinct from CSID BF status bit7. |
| BUS mask0 / clear0 / status0 | `0xc18 / 0xc20 / 0xc28` | Exact VFE680 BUS IRQ register contract. |
| BUS mask1 / clear1 / status1 | `0xc1c / 0xc24 / 0xc2c` | Exact second BUS IRQ register contract. |
| BUS global clear command | `0xc30`, clear bit `1` | Source-defined acknowledgement command. |
| consumed address support | `support_consumed_addr = true` | Hardware contract provides identity-strengthening address evidence. |

The generic VFE BUS v3 completion handler does not infer completion from software queue activity. In its top half it tests the output's composite-done mask against BUS IRQ status0. Only on that hardware bit does it read the output WM's `addr_status_0` into `last_consumed_addr`. Its bottom half then reports `res_id`, `comp_grp_id` and `last_consumed_addr` with `CAM_ISP_HW_EVENT_DONE`.

For WM16 STATS_BAF on VFE680 this means the reference hardware contract is:

**BUS status0 bit7 + WM16 ADDR_STATUS0**, with WM16 belonging to **composite group 7**.

This is distinct from the already observed **CSID1 BUF_DONE bit7**. Equal bit numbers in two different interrupt domains do not make them the same interrupt or completion fence.

## C3C/C40 ambiguity closed

Older E004ox work correctly refused to treat original Windows selected-window writes at base+`0xc3c` / base+`0xc40` as Linux BUS IRQ clears because accepted CAMSS uses `0xc20` / `0xc24`.

The exact Qualcomm VFE680 hardware table now resolves that ambiguity: `0xc3c` and `0xc40` are entries in the VFE680 `if_frameheader_cfg[]` array, while BUS IRQ clear0/clear1 are independently defined as `0xc20`/`0xc24`. Therefore the old Windows writes must **not** be transplanted or described as canonical BUS IRQ clears.

## What this does NOT prove

This experiment is deliberately static. It does **not** prove:

- that SP11 Linux currently receives VFE1 BUS status0 bit7 for a rear frame;
- that a live Windows BF FIFO8 entry and a live WM16 completion refer to the same frame/generation;
- that a particular WM16 consumed address belongs to the queued rear BF object;
- that current accepted Linux CAMSS owns/acks the VFE BUS interrupt safely;
- DMA/IOMMU quiescence and buffer reuse safety on SP11;
- full six-group rear processed-frame completion;
- front/rear VFE1 ownership handoff under the proposed native rear path;
- authorization to remove the current rear-hardware-ISP runtime denial.

## Next smallest experiment

Do **not** reboot to Windows or run KD merely to repeat the BF event proof.

The next engineering step is an **isolated, non-retiring Linux VFE680 BUS observer candidate** built from the accepted SP11 source. It should be designed around the source-defined VFE680 BUS status0 bit7 / WM16 ADDR_STATUS0 contract, with no buffer completion/release and no guessed IRQ writes. Before any load or hardware run, we must determine the existing IRQ ownership/ack path so the observer cannot double-ack or steal an interrupt. Only after source review and offline build verification should a separate one-shot non-Golden runtime experiment observe real SP11 values.

A future runtime may promote a completion only if the hardware witness is correlated with the existing owner/generation/FIFO8 identity gates; a naked BUS bit7 or address read is telemetry, not permission to free/reuse a buffer.
