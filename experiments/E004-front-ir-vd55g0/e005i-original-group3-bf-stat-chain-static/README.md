# E005i — exact original BF → GROUP3_STATS → Windows STAT metadata chain

**SP11, 2026-09-25. Parent E005h Git `b749b4f90c64f69daaccfee6634a743f2be8bcfa`.** This is source-backed static analysis of the exact same-machine OEM Windows binaries plus the already-published E005h user-mode physical endpoint. No kernel debugger or kernel breakpoint is used.

Pinned originals:

- `qccamisp8380.sys` SHA-256 `64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c`
- `surfacecamavs8380.sys` SHA-256 `b97c4338c7c8868b9f3b73a34f6aea338ae6ab2a773bfd65f3b8fd31941577ed`

## Exact ISP-side GROUP3 construction

In the original ISP, GROUP3 sender RVA **0x26170** pops its aggregate software queue (index 4), calls the existing outstanding-buffer matcher RVA **0x25078**, and constructs six possible event/resource entries.

The first five entries are generated arithmetically from resource base `0x300c` and event base `0x0e`:

| Event | Resource |
| --- | --- |
| 0x0e | 0x300c |
| **0x0f** | **0x300d** |
| 0x10 | 0x300e |
| 0x11 | 0x300f |
| 0x12 | 0x3010 |

A sixth possible entry is **event 0x0d → resource 0x301c**. The sender then stamps raw message ID **0x19 (25)** and dispatches the packet onward. Existing exact-source evidence independently identifies event **0x0f**, resource **0x300d**, FIFO group **8**, and WM **16** as BF. Therefore BF is source-locked as a member of the original GROUP3 statistics aggregate.

The matcher return is retained into the GROUP3 record but the sender has **no CBZ/CBNZ non-null gate on that matcher result** before packet construction. GROUP3 presence is therefore not itself proof of a non-null matched WM16 buffer or of DMA completion.

## Exact all-stats gate

GROUP3 sender RVA `0x26170` has one direct dispatcher caller: **RVA 0x1fe44** inside the original ISP dispatcher `0x1ef90`.

Immediately before that call:

1. the dispatcher calls RVA **0x25190**;
2. byte-normalizes its return;
3. compares it to exactly **1**;
4. skips GROUP3 unless it equals 1.

RVA `0x25190` is source-locked by the original diagnostic **“All Stats interrupts received…”**. It searches up to six request-tracking slots, increments that slot's consumed count, compares consumed count against the configured expected count, returns 1 on equality, and clears the tracker. This is a **software aggregate-completion gate for the configured statistics set**, not an independently trusted per-WM hardware DMA fence.

## AVStream / STAT route

The exact original AVStream driver source-locks:

- raw ID **7** = `IFE_MSG_ID_DUAL_PD_STATS`;
- raw ID **25** = `IFE_MSG_ID_GROUP3_STATS`;
- raw ID **26** = `IFE_MSG_ID_GROUP4_STATS`.

All three normalize through `ParseIFEMessage` to notification type **4**. An additional raw ID 27 also normalizes to type 4 but is deliberately left unnamed because no first-party label has been source-locked. Raw ID 28 is the source-labeled **FD Frame Done** route and also normalizes to type 4.

`CDispatchHandler::OnIspNotification` sends normalized type 4 to **`CCaptureFilter::ProcessStatsFrame` RVA 0x57c0**. The StatsPin writer emits QCOM custom Windows camera metadata, including item **0x8000000f / size 0x8a0** (and a second item 0x8000000e / size 0x10). This is not an opaque raw BF DMA surface.

E005h physically demonstrated the corresponding original Windows companion **STAT** pin active alongside rear NV12 3840×2160 VideoRecord, using user-mode-only CDB/FrameServer tracing and no kernel debugger. E005i does **not** claim that E005h dynamically observed raw ID25 specifically; it source-locks the route that raw GROUP3 would take to that endpoint.

## Porting consequence

The native rear design should model BF as one member of a frame/generation-scoped **statistics aggregate**, rather than treating CSID bit7, a software callback, GROUP3 emission, or the Windows STAT pin as an independent BF DMA fence. This strengthens the existing E004nv/E004px six-group architecture and the “all other groups completed” requirement.

Still missing before native processed rear ISP can be armed:

- one same-frame FIFO8 group8 entry with independently validated copy/identity;
- a **non-null** outstanding WM16 match for that exact owner/frame/token;
- independently trusted correct-buffer WM16 hardware completion/IRQ/ACK;
- DMA/IOMMU quiescence and safe stop/reuse;
- exclusive shared CSID1/VFE1 ownership.

Native rear hardware ISP remains **DENIED**.

Run:

`PYTHONDONTWRITEBYTECODE=1 python3 verify.py`

Expected:

`PASS_E005I_EXACT_OEM_BF_GROUP3_STAT_CHAIN_39_RESULT_MUTATIONS_MATCHER_NONNULL_NOT_PROVEN_DMA_FENCE_NOT_PROVEN_REAR_DENIED`
