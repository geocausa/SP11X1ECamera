# E004ol — selector 0x809 has its own original ISP-manager default dispatch path

**2026-09-24; parent E004ok Git `8e44573697338436d012c65ca2d00548a43ab0cb`.** Same-SP11 original OEM `qccamisp8380.sys`, pinned SHA; exact ARM64 evidence **S/static** only. All original code and diagnostics remain local to SP11; no OEM binary, bulk disassembly, KD material, image or DMA address is copied to the repository or another host.

**Linux responsibilities:** L1 exclusive shared ISP owner, L2 core configuration and stop lifecycle, L3 IRQ/DMA buffer ownership. Target Windows client/mode: rear OV13858 **3840×2160 VideoRecord**, but no proof of that live instance's selected core list or 0x809 invocation. The native Linux rear ISP experimental sources remain compiled but runtime-DENIED.

## Independent path, not analogical decoding

The original ISP pool-installed hardware-manager function RVA`0x15D70` preserves its selector in w24 at `0x15DB4`. Exact conditional comparison/branch chains exclude **0x80C**, **0x808**, **0x804**, **0x805**, **0x803**, and **0x802**, in that order, before reaching the **generic/default branch RVA`0x1932C`** for **0x809**. There is **no 0x809-specific comparison** in this source-checked dispatch path.

Within that default branch, source at `0x19350–0x19364` limits the per-iteration *normal nonnegative* configured list count to at most two; `0x19368–0x19388` reads the manager's configured list beginning at index six and accesses 0x30-byte per-core records. An original signed comparison rejects a core ID >=4; **a nonnegative lower bound is NOT established by that comparison alone**. `0x1938C–0x193C8` skips a disabled record, loads a record instance pointer, fetches its callback pointer, preserves original selector **w1=w24** and makes an indirect call. **Loading an instance pointer is not a separate proof of a null check.** The branch observes a returned status and iterates; this does not identify any receiving core's interpretation or completed hardware effect.

~~~mermaid
flowchart TD
    S["Original nested manager selector in w24"] --> A{"0x80C / 0x808 / 0x804 / 0x805 / 0x803 / 0x802?"}
    A -->|"specific match"| D["Dedicated case, independently characterized only where verified"]
    A -->|"0x809: no match"| G["Generic/default branch 0x1932C"]
    G --> L["Read bounded configured list starting at index 6; per-core enabled check"]
    L --> F["Forward original selector 0x809 as w1 to selected callback"]
    F --> U["Receiver body, live selected cores, return semantics & DMA effects UNKNOWN"]
~~~

This establishes **software routing** of 0x809 to *potential* selected original per-core interfaces, **not** that the selector is equivalent to 0x805, is a stop command, always reaches CDM/IFE/CSID or that the callback actually runs during the live rear session. If a list is empty or a record disabled, it may not invoke a core at all. Do not translate 0x809 into a native Linux ioctl or release of a DMA buffer.

## Verification and next falsifiable gate

`PYTHONDONTWRITEBYTECODE=1 python3 verify.py` checks original same-SP11 OEM SHA, **58 exact ARM64 anchors**, 12 negative tests (including a deliberately altered callback-forwarding instruction), the independent E004oe conservative 0x809 status and exact 0x809 fallthrough relative to the six explicit cases. `RESULT.json` is scalar/static-only.

**Next independent receiver gate:** establish which concrete manager list elements (index six/seven) and per-core callback bodies can receive the default branch for selector 0x809, then source-trace their argument/return contracts without assuming that the already known 0x804/0x805 handlers behave the same. Separately trace later IFE stop-progress/event, BF/WM16 bus/IRQ and actual per-buffer DMA retirement. Only a bounded and permitted *same-session* Windows rear 4K observation can establish the active configured list and live 0x809 path. Do not retry the blocked KD debugger workflow.

**Still unproven:** live Windows rear VideoRecord dispatch of 0x809, live BF event 0x0F/FIFO8 WM16 DMA retirement, safe native Linux rear processed ISP 4K optical frames or front↔rear PIX shared-owner completion. Protected Golden, front 27-frame native PIX, rear RAW/software-4K fallback and IR privacy unchanged.
