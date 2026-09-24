# E004ot — four original resource labels and corrected IFE1 selector; distinguish existing live VFE1 evidence

**2026-09-24; parent E004os Git `572dffb31238265c1fba12d4604764ce4939ff89`.** Original same-SP11 OEM ISP image SHA-locked and inspected read-only, four short original descriptor names/PE jump-table bytes checked in place; no OEM driver image/bulk disassembly, physical/DMA addresses, images, firmware, KD credentials/logs or proprietary tuning exported. Linux responsibility **L1 exclusive shared PIX/VFE owner, L2 correct per-IFE MMIO resource, L3 safe WM/IRQ/DMA buffer lifetime**. Explicit target Windows client/mode: rear OV13858 NV12 3840×2160 VideoRecord. Evidence: **S** = source-locked original Windows code, **P** = separately completed live Windows physical register observations from E004nq. Do not conflate these evidence classes.

## Actual resource names and the previously unexamined selector 1

Original IFE initialization includes a branch at RVA`0x223C4` that passes its validated instance index `w24` (values `0..3`) to source-verified resource lookup `0x2B568`; it is **not restricted to 0, 2, 3**. E004or verified 0,2,3, and E004os traced mapped-pointer producers, but their bounded scope did not independently cover selector 1. E004ot checks all four actual original PE signed-byte jump-table destinations, their pointer-array reads and the short descriptor labels used by the conditional `MmMapIoSpaceEx` producers:

| Original lookup selector | Jump branch, original ISP RVA | Actual descriptor name tied to mapping producer [S] | Global resource array and entry |
| --- | --- | --- | --- |
| **0** | `0x2B590` | `IFE0` | Global table `0x4AEE0 +0x50`, first pointer |
| **1** | `0x2B5A4` | `IFE1` | Global table `0x4AEE0 +0x50`, second pointer |
| **2** | `0x2B5B8` | `IFELITE0` | Global table `0x4AEE0 +0x20`, first pointer |
| **3** | `0x2B5C8` | `IFELITE_CDM0` | Global table `0x4AEE0 +0x20`, second pointer |

The resource names are checked as exact four short null-terminated labels at original source RVAs `0x2FFE8`, `0x30010`, `0x30018`, and `0x30048`, respectively. The conditional original resource-matching and `MmMapIoSpaceEx` return stores are verified independently at E004os RVAs `0x31DC`, `0x3214`, `0x3270`, `0x32F4`. The source *naming/mapping relationship* is proven; it does **not** establish that any particular callback's pointer was selected in a live rear session or that an OEM display name alone establishes the physical device's active session identity.

## What is already physically proven — and what is not

The existing accepted [E004nq live Windows physical-register oracle](../e004nq-rear-physical-mmio-5phase/README.md) **already measured VFE1 active** in **both** same-SP11 rear 3840×2160 VideoRecord windows (with ten enabled image/stats write masters, including BF WM16), while VFE0 had no active write masters. Windows rear processing used CSID1/VFE1 in those measured sessions, even though an *older* E004nl Linux source-only candidate assumed CSID0/VFE0. The older assumption must NOT override the later live physical result.

**Still missing:** the original OEM IFE manager's *runtime-chosen lookup selector, actual IFE context+0x140 mapped pointer and +0x6B678 zero/nonzero mode* in that same live rear session. Static evidence makes the selector-1/IFE1 route available, but does **not** establish that this callback or that selector was used during E004nq's physical measurement. The live BF event `0x0F`/FIFO8, WM16 bus/IRQ stop and physical DMA-buffer retirement remain unproven, and no Linux-native rear hardware ISP 4K optical frame has been captured.

## Reproducibility and gate

Run `PYTHONDONTWRITEBYTECODE=1 python3 verify.py`. It checks original same-SP11 OEM ISP SHA and **73 exact ARM64 instruction anchors**, four short descriptor-label strings and **four actual original PE jump-table byte destinations**, E004os conditional genuine MMIO mapper, the existing E004nq **P/live VFE1-active and VFE0-inactive** facts from its already committed scalar results, plus **16 fail-closed negative mutations**. Only safe derived names/RVAs, pre-existing qualitative physical observations and false/unproven gates enter `RESULT.json`; no original OEM binary, original bulk disassembly, private physical/DMA addresses, optical data or KD logs are copied into Git.

**Next falsifiable gate:** source-identify the OEM per-IFE instance index/threshold for the active rear VideoRecord through permitted evidence without retrying/bypassing the previously blocked KD debugger launch. Independently trace whether the WM16 bus and IRQ status plus generation-matched BF/statistics buffer are truly retired after original finalizer register writes. Only portable verified safety outcomes belong in a clean kernel CAMSS/V4L2 driver; do not transplant Windows services, opaque selectors or proprietary ISP code. The experimental native Linux rear ISP remains source-compiled but runtime DENIED. Protected Golden, working front native PIX, rear RAW/software-4K fallback and IR safeguards are unchanged.
