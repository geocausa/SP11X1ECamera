# E004oh — ISP stop request versus independent progress and completion paths

**2026-09-24; parent E004og, Git `03d7b1817f0606f06a6f4947a0474843326c00c7`.** Same-SP11, original Qualcomm OEM ISP ARM64 `qccamisp8380.sys`, investigated **statically and read-only**. This follows the [permanent Windows→native Linux stack map](../../../docs/CAMERA-STACK-PORT-MAP.md) without starting any camera, loading a module or touching Golden. The purpose is to determine which hardware-block stop and buffer-lifetime facts our clean Linux camera driver must verify, not to copy Windows AVStream/Frame Server/AI plumbing.

## A returned top-level stop command is not the end of the original code's stop lifecycle

The prior [E004og](../e004og-original-isp-three-core-callback-implementations-static/README.md) identified three *real* original CSID, IFE and CDM core-function implementations. The original ISP's eligible manager stop-like branch issues them in the **software** order CSID→IFE→CDM, subject to state and error guards. E004oh separately traces **what happens inside and after those calls**.

| Hardware stage | Original same-SP11 code evidence | Consequence for native Linux |
| --- | --- | --- |
| **IFE — initial stop-like core call** | Its `0x805` receiver, original ISP RVA `0x22CD0`, calls a pre-stop helper at **`0x221A0`** from `0x23618`, branches on return at `0x23620`, and invokes a **different** stop/resource helper at **`0x27278`** from `0x23644` with independent result handling. The first helper itself calls another original routine at `0x221D0` and checks its result. | Do not substitute one unguarded “ISP off” operation for both. Neither a first helper's return nor an outer AVStream StopAsync result establishes safe DMA surface release. |
| **IFE — per-resource stop and independent later progress** | The second helper marks stop work active at `0x272A0`, bounds a per-resource loop at **`0x272C8`**, makes guarded indirect resource calls, then clears state and invokes an independent callback around `0x27334–0x27358`. A **separate** original completion/progress handler at `0x1F230–0x1F254` checks/clears its progress flag and invokes `0x241D8`, which has its own event-related result checks at `0x2422C–0x24230`. | Model **request → per-output quiesce → independently observed completion/drain → retire**. The identities of every called helper, IFE interrupt source, active image/statistics WMs and safe quiescence predicate are still a separate source/runtime verification gate. |
| **CSID — pending work and worker progress** | A CSID completion path at `0x1BCAC–0x1BCE0` checks remaining status, atomically decrements a pending counter with an exclusive load/store loop plus memory barrier, and takes a separate branch when work remains. The CSID stop-like core code has distinct state-clear and event/worker-related calls at `0x21B00–0x21B1C`; its later helper at `0x21B68` is separately conditional. | A CSID input-stop request, its queued interrupt/work accounting and confirmed stopped ingress must remain separate. **CSID pending counter reaching zero does not prove VFE WM16, BF FIFO group8 or the image DMA bus is quiescent.** |
| **CDM — command/worker state** | Its original `0x805` receiver at `0x2853C–0x285A4` clears a command-state field, sets another session state and invokes a distinct event-related helper. | Command engine state is its own completion condition; it is **not** a surrogate for CSID ingest or IFE image/statistics buffer retirement. |

~~~mermaid
flowchart TD
 R["App / AVStream stop request"] --> M["ISP manager: conditional CSID → IFE → CDM dispatch"]
 M --> C["CSID: pending work + worker/event progress"]
 M --> I["IFE: pre-stop helper → bounded output/resource helper"]
 M --> D["CDM: separate command state/event"]
 I --> Q["Independent IFE stop progress/event path"]
 C --> G["Native Linux safety gate"]
 Q --> G
 D --> G
 G --> X["Only AFTER hardware-specific IRQ/DMA stop proof:<br/>retire actual enabled image + metadata + statistics WMs"]
~~~

**The final gate in that diagram is a design requirement, not an observed Windows runtime result.** The source-only discovery does not identify exact VFE WM stop/IRQ acknowledgement registers, command queue DMA lifetime or evidence that the physical rear BF event `0x0F` ran in any real Windows 4K recording. Our E004nv mode-0 event/group8/WM16 handler remains static-only; a live mode may differ. Separately measured Windows rear NV12 4K application handles are not proof of Linux native rear hardware ISP optical pixels.

## Concrete next slice

The highest-value next investigation is now **the specific IFE stop-resource callback invoked by `0x27278`** and its associated interrupt/WM bus acknowledgement and per-request output lifetime. Match that against the known rear 4K **enabled ten-WM** snapshot, isolate BF/WM16 from ordinary image outputs, and verify a single same-session Windows capture's true IRQ dispatch mode and stop conditions before installing any Linux rear PIX driver. CSID's pending-work path and CDM's command path must remain separately accounted for; `0x809` still has no source-decoded meaning. The front native PIX and rear RAW/software fallback have their own validated lifecycle and should not be displaced by this experimental rear hardware-ISP graph.

## Verification and non-regression

`PYTHONDONTWRITEBYTECODE=1 python3 verify.py` SHA-locks the exact original private OEM ISP image and checks **45 original ARM64 instruction anchors** connecting first IFE stop to its two helpers, per-resource bounded iteration, independent IFE progress, CSID atomic pending state and distinct CDM event state. It runs **14 fail-closed negative tests** against invented hardware completion, Linux rear 4K, live BF, `0x809`, Golden changes and private export. [RESULT.json](RESULT.json) contains safe derived RVAs and conservative truth values only, never original OEM binaries, raw original disassembly, pixel data, DMA addresses or private KD logs.

**No device runtime was exercised**; protected Golden FullIO v19c, native front PIX, independent rear RAW/software-4K and IR privacy safeguards remain unchanged.
