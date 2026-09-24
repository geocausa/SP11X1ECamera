# E004oo — original later IFE progress callback signals a Windows event, not a WM16 DMA fence

**2026-09-24; parent E004on Git `45b1abd531bd980223734b849dd1c1b85acc6097`.** Exact original same-SP11 OEM `qccamisp8380.sys` is SHA-pinned and read-only. This is **S/static original software evidence**. Intended native Linux slices: **L1** exclusive ISP owner, **L2** IFE stop lifecycle, **L3** per-WM/stats IRQ and DMA-buffer retirement. Desired Windows oracle is rear OV13858 **3840×2160 VideoRecord**, but its live mode, BF event, actual IFE stop/progress execution and DMA retirement remain unobserved.

## Source-verified conditional chain

E004oh previously identified an IFE later progress handler RVA`0x1F230` and helper RVA`0x241D8` but did **not** identify the latter's event mechanism. E004oo resolves the bounded call sequence:

| Original source | Exact static result | Does NOT prove |
| --- | --- | --- |
| RVA `0x1F230–0x1F254` | Checks IFE context flag at `+0x171`. If nonzero, clears that byte at 0x1F244 and calls progress helper 0x241D8 at 0x1F254. | That the live Windows rear 4K stop reached this branch, or that flag clearing equals a completed WM16 bus/IRQ drain. |
| **Entire 33-instruction helper** RVA `0x241D8–0x24258` | Checks nonnull context, emits diagnostics, passes context+`0xC8` to event-wrapper RVA `0x2A1D8`, checks the wrapper's software status and may log an error. **No WM16 register read/poll, DMA wait, or direct interrupt acknowledgment appears in this full helper.** | That the event could not have been triggered by another independent hardware-driven source, or that other IFE stop/IRQ/retirement paths do not exist. |
| RVA `0x2A1D8–0x2A218` and **original ntoskrnl.exe import table** | Wrapper checks its input/event pointer, then loads original IAT slot RVA `0x3F2E8`, independently resolved to **`KeSetEvent`** (NOT `KeWaitForSingleObject` at `0x3F060`, NOR `KeClearEvent` at `0x3F250`). It passes zero increment/Wait parameters, performs the event signal and returns wrapper status; a missing pointer has a separate failure return. | A kernel hardware-completion fence, verified DMA address retirement, or proof that signalling succeeded in any live rear session. |

The software-event signal could be part of a larger, as-yet-untraced hardware-driven completion path; **do not infer that it is inherently premature or that no other hardware acknowledgment exists**. This finding only closes the immediate helper's identity and rejects an unsafe inference: neither `IFE context +0x171 == 0` nor a signalled event, in isolation, authorizes Linux to free BF/WM16 or other in-flight image/statistics buffers.

## Reproducibility and explicit next gate

Run `PYTHONDONTWRITEBYTECODE=1 python3 verify.py`: validates SHA of original same-SP11 ISP, **60 exact ARM64 instruction anchors**, *every instruction* in the 33-instruction later helper, three independently resolved original ntoskrnl IAT symbol slots for KeSetEvent/KeWaitForSingleObject/KeClearEvent, original E004oh conservative progress identity, and **11 fail-closed negative mutations**. Only safe derived scalar RVAs/flag and software API identity plus conservative false gates appear in `RESULT.json`. Original private executable, bulk disassembly, firmware, KD credentials/logs, DMA addresses, optical imagery and camera image hashes remain absent from Git.

**Next falsifiable evidence:** trace the independent producer of IFE context flag `+0x171`, the WM16 bus write-master disable/IRQ status and the *specific per-buffer or per-generation hardware retirement predicate*, accounting separately for VFE image outputs and stats FIFO8/BF. Confirm same-session Windows rear selected zero/nonzero IFE mode and whether BF event `0x0F`/FIFO8 actually occurs by a permitted non-KD method if possible; never retry/bypass the blocked KD debugger launch. Only independently verified physical effects belong in clean native CAMSS L1–L3, with safe fault handling if quiescence cannot be proven. No Windows selectors/services/Studio Effects or AI dependencies should be transplanted.

**Non-regression:** existing experimental native Linux rear ISP source remains runtime-DENIED. No camera process/device, boot configuration, firmware, protected Golden, front 27-frame PIX, rear RAW/software-4K fallback or IR safeguard was altered.
