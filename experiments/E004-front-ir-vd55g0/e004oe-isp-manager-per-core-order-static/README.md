# E004oe — original ISP manager’s CDM, IFE and CSID dispatch order

**2026-09-24; parent E004od, Git d3ce9c8a953295daeaaeaa404df9ffadeaa03546.** Read-only, same-SP11 original OEM Windows ARM64 ISP static evidence. This is an addition to the permanent [Windows-to-Linux camera-stack map](../../../docs/CAMERA-STACK-PORT-MAP.md); the objective is a native, controllable Linux CAMSS/V4L2 driver, **not** emulation of Windows services or reproduction of vendor AI effects.

## Precisely what the original code establishes

E004od identified the ISP hardware manager’s installed nested callback at driver-relative RVA **0x15D70**. E004oe checks the six subsequent **indirect core-interface calls** and identifies their respective hardware block using **both their exact selector call sites and their source-code failure-diagnostic cross-references**. The proprietary diagnostic text stays in the original SP11 binary; the committed verifier checks each diagnostic’s original RVA, byte hash and two-instruction reference.

| Hardware-manager branch | Checked source dispatch order | Core interface dispatch instruction → checked failure-diagnostic code RVA |
| --- | --- | --- |
| Selector **0x804**, branch **0x15EE0** | **CDM → IFE → CSID** | CDM: **0x15F50 → 0x15F5C**; IFE: **0x15FEC → 0x16234**; CSID: **0x16208 → 0x162AC** |
| Selector **0x805**, branch **0x16300** | **CSID → IFE → CDM** | CSID: **0x163C8 → 0x163D8**; IFE: **0x16434 → 0x16448**; CDM: **0x164B4 → 0x164C8** |

The first start-like call conditionally precedes an IFE loop, which conditionally precedes a CSID loop. The stop-like branch has separate CSID, IFE and CDM calls and distinct return handling. The three lower blocks are not interchangeable: CDM is the camera command/processing machinery; IFE is the image front-end hardware; CSID receives/routes the CSI input. This **software call-site order is not a measured physical timestamp or DMA-completion guarantee**, nor proof that all stages were eligible in a particular camera profile.

~~~mermaid
flowchart TD
 A["AVStream selects a camera backend/profile"] --> B["ISP outer callback (conditional route)"]
 B --> C["ISP hardware-manager callback 0x15D70"]
 C --> S["0x804 start-like branch"]
 C --> T["0x805 stop-like branch"]
 S --> SC["CDM per-core interface"]
 SC --> SI["IFE per-core interface"]
 SI --> SS["CSID per-core interface"]
 T --> TS["CSID per-core interface"]
 TS --> TI["IFE per-core interface"]
 TI --> TC["CDM per-core interface"]
 SS --> X["Actual per-core handler / hardware completion still to be traced"]
 TC --> X
~~~

### Required Linux behaviour versus Windows-only plumbing

Linux **must** implement validated sensor mode/power/CSI routing, exclusive CSID1/VFE1 ownership, appropriate command submission, real IFE/bus/DMA/IRQ completion and safe release of every enabled output before reuse. A native driver should reproduce these *verified hardware and safety contracts* through the Linux media-controller/V4L2 and CAMSS ownership model—not copy OEM Windows interface GUIDs, selectors, Frame Server, Device MFT, Studio Effects, or AI processing.

**Do not simply hard-code “CDM, IFE, CSID” into Linux based on this table.** Our existing native front PIX and rear RAW/software pipeline have their own validated ordering; these Windows branches can skip individual stages or issue asynchronous operations. We still need to trace the actual lower-level CDM/IFE/CSID callback bodies, parameter/return ABI, queued command/bus/CSI side effects, IRQ and DMA retirement, abort/rollback and the rear ISP profile’s actual Windows selection. The separate **0x809** selector remains unidentified. BF event **0x0F**, FIFO group 8, WM16 statistics-buffer completion and Linux-native rear **3840×2160 hardware-ISP optical frames** remain unproven.

## Reproducibility, limitations and machine safety

`PYTHONDONTWRITEBYTECODE=1 python3 verify.py` SHA-locks the exact original same-SP11 ISP binary, checks **55 original ARM64 instructions** at the conditional branches, six indirect calls, associated failure-diagnostic address references, and core-array setup; checks the six original diagnostic byte hashes without exporting their OEM text; and exercises **13 fail-closed negative mutations** rejecting altered order, false hardware/MMIO claims, invented Windows runtime observations, fabricated native rear 4K or modified Golden. `RESULT.json` contains only scalar RVAs, hashes and conservative evidence flags. No original driver bytes, raw disassembly, optical pixels, DMA addresses, KD material, live camera activity, kernel installation, module loading or reboot.

**Next bounded static task:** starting from the six source-backed per-core indirect-call sites, follow how CDM, IFE and CSID core-interface arrays are populated and identify each actual callback implementation and argument/return structure. Separately trace **0x809** and the safe-stop acknowledgement/WM16 retirement contract. A bounded non-image Windows mode/profile comparison can later test whether rear video, preview, photo and camera switching actually select these branches. Keep Golden FullIO v19c, front native PIX and rear RAW/software-4K fallback intact.
