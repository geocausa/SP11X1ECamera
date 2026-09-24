# E004oi — the IFE stop-resource callback selection reaches the BF statistics port

**2026-09-24; parent E004oh, Git `f94618a4b030a5fd0d6d53d206894dc7100f4efb`.** Source-only, read-only static study of the exact original same-SP11 OEM ARM64 `qccamisp8380.sys` in the original archived Windows driver package. This advances [the canonical Windows→native Linux camera-stack port map](../../../docs/CAMERA-STACK-PORT-MAP.md) without an actual Windows capture, camera MMIO/DMA, kernel installation, optical pixel access or Golden modification.

## The previously anonymous resource callback now has two conditional implementations

[E004oh](../e004oh-isp-multistage-stop-progress-static/README.md) traced the original IFE `0x805` receiver through its bounded per-resource stop helper at RVA **`0x27278`**, which reads the resource ID in `w1`, passes the stop-like flag **zero** in `w2`, and calls the resource callback stored in the IFE instance field at offset **`0x6B688`** (callback read **`0x272E4`**, indirect call **`0x27300`**).

E004oi follows the **original producer of that same callback field**. An IFE initialization function compares a mode/state field at **`0x6B678`** to zero (original instruction **`0x19FB0`**) and **conditionally installs one of two distinct original code addresses** using an ARM64 select at **`0x19FE0`** and a store into **`0x6B688`** at **`0x19FE8`**.

| Selection in original ISP source | Actual original resource callback | Distinguishing source fact |
| --- | --- | --- |
| Mode/state field **nonzero** | **RVA `0x1C0F0`** | The handler receives resource ID and an enable/disable flag, branches on its own resource IDs and writes mode-dependent control fields. |
| Mode/state field **zero** | **RVA `0x1D830`** | This alternative also receives resource ID and an enable/disable flag, but has an **explicit `0x300D` resource comparison** at **`0x1D850–0x1D860`**, followed by its own guarded resource dispatch. |

The *two original functions* `0x1C0F0` and `0x1D830`, and the source-verified per-resource caller `0x27278`, are independently present as ARM64 PE function entries in the **exact same-SP11 OEM ISP binary**. This closes the missing link between the **original ISP stop-resource manager** and a **specific original callback that recognises resource `0x300D`**, the **same numeric BF statistics resource port** independently identified in [E004nv's static BF event path](../e004nv-rear-six-group-bf-static/STATIC-BF-CALLCHAIN.md).

~~~mermaid
flowchart TB
    W["Windows AVStream → ISP 0x805 stop-like path"] --> I["IFE original first callback 0x22CD0"]
    I --> R["Bounded resource helper 0x27278"]
    R --> P["IFЕ instance resource callback field +0x6B688"]
    S["Original IFE mode/state +0x6B678"] --> Q{"Zero?"}
    Q -->|nonzero| A["Original callback 0x1C0F0"]
    Q -->|zero| B["Original callback 0x1D830"]
    A --> P
    B --> P
    B --> BF["Explicit BF-associated resource ID 0x300D branch"]
    P --> G["Still required: matching real Windows mode, BF/WM16 DMA/IRQ stop proof"]
~~~

**This is static conditional software routing, NOT evidence that live rear 4K selected the zero state or executed the BF branch.** The numeric BF-associated `0x300D` branch in a resource handler is also **not** proof that BF event `0x0F` arrived, that FIFO group8 held a completed buffer, that the IFE bus actually stopped, or that WM16 DMA is safe to retire. The other callback `0x1C0F0` should **not** be labelled “no BF”: lack of its *same explicit comparison* is not proof that BF is disabled or never completes through another route.

## What this means for the native Linux port

The permanent port map can now distinguish **(a)** selecting a camera/profile, **(b)** selecting original ISP mode/state and a resource-specific callback, **(c)** invoking the stop-like callback on the enabled output resource list and **(d)** independently proving physical DMA/IRQ quiescence. For Linux we need only the **verified hardware and lifetime contracts** in native CAMSS/V4L2; do not reimplement Windows' GUID selector, AVStream/Frame Server, proprietary driver binary, Device MFT, Studio Effects or AI image processing.

**Next exact task:** source-trace the two original resource callback bodies, especially the alternative `0x1D830` branch for **`0x300D`** when called with zero (stop flag), to the *actual hardware register/IRQ/statistics bus write-master stop and acknowledgement*. Compare the chosen callback and active resource list in a bounded real Windows rear 4K capture before promoting any static BF or WM16 statement to a live fact. Also resolve which of the already observed ten Windows rear VFE write masters belong to the active mode’s image, metadata and statistics drain set. A callback returning and a CSID pending counter reaching zero are insufficient alone.

## Reproduce and verify the limits

`PYTHONDONTWRITEBYTECODE=1 python3 verify.py` SHA-locks the exact original same-SP11 OEM ISP image, checks **35 original ARM64 instruction anchors** for conditional callback creation, the bounded resource stop dispatch, original resource ID `0x300D` and the two original PE function entries; runs **16 fail-closed negative tests** for fabricated live rear session selection, BF completion, WM16 DMA retirement, native rear 4K, MMIO proof, Golden changes or private export. [RESULT.json](RESULT.json) contains only source-derived scalar RVAs and conservative state flags. No original private Windows code, disassembly, binaries, logs, optical pixels, DMA addresses, firmware or KD credentials enter Git.

Golden FullIO v19c, front native PIX, rear RAW/software-4K fallback and IR safety remain untouched. Linux rear hardware-ISP 3840×2160 optical output and live Windows BF/WM16 completion remain **unproven**.
