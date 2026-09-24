# E004oj — BF resource stop-zero write reaches the independent WM16 CFG0 offset

**2026-09-24; parent E004oi, Git `eae01b8655fb77c7bb3daa59ccd9f7f3fd37ff6c`.** Original **same-SP11** OEM Qualcomm ARM64 ISP binary studied **offline, read-only**. This source-locked trace supplies a concrete, *conditional register-write* link between original IFE resource stop and the previously static BF/WM16 control register. It does **not** claim a live rear VideoRecord session selected that branch or proved a safe DMA stop.

## Exact original source chain

[E004oi](../e004oi-ife-resource-callback-bf-port-static/README.md) established that the IFE per-resource 0x805 stop loop selects one of two original callbacks: **zero-state callback `0x1D830`**, or nonzero-state callback `0x1C0F0`. The selected zero-state callback explicitly recognises BF-associated resource **`0x300D`**.

**E004oj establishes the register-window arithmetic, branch destination and value:**

| Evidence in original same-SP11 ISP | Derived static result | What this is NOT |
| --- | --- | --- |
| The IFE initializer loads a source base pointer from device context `+0x140` at code RVA **`0x22440`**, compares the device instance against a mode/threshold at **`0x2246C`**, and stores a zero/nonzero selector at context offset **`+0x6B678`**. It chooses between **`+0xC00`** and **`+0x1200`** at **`0x2247C–0x22488`**, saving the selected register-window pointer at context **`+0x150`** (RVA `0x2248C`). | **Zero-state selects original base +`0xC00`**; nonzero-state selects base +`0x1200`. | The live rear 4K instance’s selected state or a device-specific, source-confirmed physical MMIO base. |
| The same zero/nonzero selector picks original callback **`0x1D830`** or **`0x1C0F0`** at **`0x19FE0`**, saved at IFE context **`+0x6B688`**. The IFE stop loop reads that exact field at **`0x272E4`**, passes resource ID and **flag zero** at **`0x272E8`**, then invokes at **`0x27300`**. | If the **zero-state** alternative is selected and resource `0x300D` is included, its **original BF-capable handler** is called with the stop-like zero flag. | Proof that the live Windows rear VideoRecord profile selected that handler or that BF was enabled there. |
| The alternate handler tests `0x300D` at **`0x1D850–0x1D860`**, then computes the enable/disable value at **`0x1D884–0x1D888`**; a zero input flag selects **zero**. Its original bounded resource jump table at **`0x1DBA4`** sends resource index **13** (`0x300D - 0x3000`) to code RVA **`0x1DA6C`**. | For this conditional stop invocation, **w21 = 0**, and the BF resource branch is exactly **`0x1DA6C`**. | Evidence of a BF IRQ event or DMA completion. |
| At **`0x1DA6C–0x1DA74`**, the original BF resource branch loads the selected IFE register-window pointer and writes that zero value to **`[selected_window + 0x1200]`**. | **Zero-state conditional total offset:** original base **`0xC00 + 0x1200 = 0x1E00`**, with a **32-bit zero write**. | A documented guarantee that zeroing CFG0 is sufficient to stop *all* in-flight data or safely retire the associated WM16 buffer. |

The total relative offset **`0x1E00`** matches the independent original-OEM [E004nv static BF direct register-read investigation](../e004nv-rear-six-group-bf-static/README.md), which maps **VFE WM16 CFG0 to VFE+0x1E00** and BF’s ADDR_STATUS0 to VFE+0x1E70; E004nv independently identified BF resource `0x300D`, FIFO group 8 and event `0x0F`. The new stop-zero path and prior BF-stat completion path therefore converge on the **same relative WM16 CFG0 address**, through different original code paths.

~~~mermaid
flowchart TB
    S["Original IFE 0x805 stop-like manager"] --> R["Bounded output/resource loop 0x27278"]
    M["IFE instance's conditional zero-state"] --> W["Register window = original base + 0xC00"]
    M --> C["Resource callback = 0x1D830"]
    R --> C
    C --> B{"Resource ID = BF 0x300D?"}
    B -->|yes; zero stop flag| Z["Source code writes zero to selected window + 0x1200"]
    W --> Z
    Z --> O["Original base + 0x1E00\nindependently matches WM16 CFG0 relative offset"]
    O --> G["Still required: active rear mode + hardware stop/IRQ + WM16 DMA retirement"]
~~~

## How this changes our native Linux engineering plan

This is a concrete **candidate native rear BF/WM16 stop-control action** from independent original-source paths, not a reason to transplant Windows AVStream selectors into Linux. Keep native CAMSS/V4L2 responsible for actual IFE/CSID/command hardware ownership, enabled image/statistics DMA surfaces, interrupt acknowledge, independently proven hardware quiescence, bounded rollback and no premature buffer free. **Do not implement “write zero at +0x1E00, therefore completed”**: E004nv BF/WM16 group8 event, DMA address status and bus stop must be validated together on a specific live rear session before enabling/releasing anything. A BF output *disabled in a different capture mode* likewise needs its own verified active-WM/IRQ/stop contract.

**Remaining precise gap:** establish the live rear Windows 3840×2160 active IFE instance and zero/nonzero callback mode, relate the initialization source base to that instance’s mapped VFE register window, and trace the *post-write* physical bus/IRQ/WM16 drain condition and stopped DMA lifetime. Live BF `0x0F`, FIFO8 buffer completion, per-frame IQ/RT-CDM and Linux native rear processed optical 4K remain unproven. No Windows AI/Studio Effects requirement is created.

## Reproducibility and safety

`PYTHONDONTWRITEBYTECODE=1 python3 verify.py` SHA-pins the exact original private same-SP11 ISP binary, checks **35 original ARM64 instruction anchors** for conditional register-window selection, callback selection, stop-zero flag, BF resource comparison, original jump-table target and actual zero write, **decodes only the source-bounded index 13 into a derived RVA**, independently checks the E004nv BF port/IRQ identity and runs **14 fail-closed negative tests**. [RESULT.json](RESULT.json) exports safe derived RVAs, offsets and conservative booleans; original proprietary driver, disassembly, raw diagnostics, DMA pointer values, optical images and KD material remain private on SP11.

All work in this experiment was **static and offline**. Protected Golden FullIO v19c, front native PIX, rear RAW/software-4K fallback and IR privacy remain unchanged.
