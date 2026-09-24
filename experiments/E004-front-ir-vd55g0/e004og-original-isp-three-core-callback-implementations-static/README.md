# E004og — three real original Windows ISP core callback implementations

**2026-09-24; parent E004of, Git fa2e06969f86d34a648b406956528a5720e8ad99.** Read-only original same-SP11 Qualcomm ISP `qccamisp8380.sys` static investigation. This narrows the native-Linux camera-stack port map from the AVStream manager, through per-core interface records, to the *original receiving functions*. No Windows Camera app, live sensor, kernel module, physical MMIO, DMA, private firmware, optical frame or Golden boot change.

## The concrete callback functions are source-backed, not inferred from diagnostics alone

[E004oe](../e004oe-isp-manager-per-core-order-static/README.md) mapped the conditional hardware-manager core **software** call order. [E004of](../e004of-isp-per-core-interface-provenance-static/README.md) traced per-core record allocation, descriptor lookup and pointer copying. E004og identifies **three specific original core-interface first callbacks** by proving **both** (a) their respective unique function address is prepared and stored into the first interface slot by that hardware-core initializer and (b) the callback function entry is present in the original ARM64 PE exception/function-entry table. Their bodies explicitly distinguish `0x804` and `0x805` in the *original binary*.

| Original core | Original initializer takes function address and stores first interface slot (driver RVAs) | Original first callback function entry | Original body’s selector branches |
| --- | --- | --- | --- |
| **CSID** | `0x17694` → `0x176A4` | **`0x211B0`** | `0x804` compare `0x218D8`; `0x805` compare `0x218E0`, stop-like branch `0x21904` |
| **IFE** | `0x2233C` → `0x2234C` | **`0x22CD0`** | `0x804` compare `0x23604`; `0x805` compare `0x2360C`, stop-like branch `0x23614` |
| **CDM** | `0x18348` → `0x1835C` | **`0x28480`** | `0x804` compare `0x28534`; `0x805` compare `0x2853C`, stop-like branch `0x2854C` |

These are **actual source-verified original handler implementations**, not a claim that all three instances were used by the **live** Windows rear 4K VideoRecord session. Original per-device availability and per-mode profile selection remain guarded by E004oc–E004of’s dynamic interface records and execution branches.

~~~mermaid
flowchart TD
    A["Windows camera client/profile"] --> B["AVStream per-GUID backend selection"]
    B --> C["ISP hardware-manager callback 0x15D70"]
    C --> D["Core-indexed callable interface records"]
    D --> E["CDM callback entry 0x28480"]
    D --> F["IFE callback entry 0x22CD0"]
    D --> G["CSID callback entry 0x211B0"]
    E --> H["Different guarded core commands and completion paths"]
    F --> H
    G --> H
    H --> L["Native Linux CAMSS L0–L3:<br/>independently verified sensor/CSI/ISP/DMA/IRQ lifecycle"]
~~~

## Why a core callback returning is not yet a safe DMA-retirement acknowledgement

**CSID `0x805`:** the original branch at `0x21904` checks state and invokes an earlier registered function pointer at `0x2192C`. Its later stop-related code at `0x21B10–0x21B34` includes a worker/event-related helper and a source diagnostic for an IST processing thread released during CSID stop; another conditional helper is called at `0x21B68`. This distinguishes a stop *request* and further progress/cleanup, without proving which physical CSID stop IRQ or full quiescence condition occurred in any live rear session.

**IFE `0x805`:** the original handler at `0x23614–0x2364C` calls **two separate functions** at `0x221A0` and `0x27278`, with independent return/error paths; nearby original diagnostics identify reset/stop-command-event failures and a distinct `DAL_ife_stop` failure. The second helper’s specific MMIO actions and the exact DMA/IRQ retirement point **still require their own source trace and runtime confirmation**. It is unsafe to free live VFE/WM buffers solely because the outer camera engine or hardware manager returned.

**CDM `0x805`:** `0x2854C–0x285A8` modifies its own command/session status, posts to a separate event-related helper and checks progress; **`0x804`** has a different branch at `0x285C8`. CDM command completion is not the same thing as IFE pixel DMA or CSID input quiescence.

The earlier E004oe **CDM→IFE→CSID** start-like manager order and **CSID→IFE→CDM** stop-like order identify *software dispatch calls*, not a proven universal physical stop sequence. Our existing front-native PIX and rear RAW/software capture modes have their own validated hardware lifecycle; do not replace them with an OEM numeric selector recipe. The BF event `0x0F`, FIFO group 8 and WM16 physical completion remain **static or otherwise unobserved** for live Windows rear 4K, and Linux native rear **processed 3840×2160 ISP optical output is not yet proven**. The separately observed Windows application NV12 4K handle counts cannot bridge that gap.

## Independent Linux porting consequences and next exact experiment

Implement necessary verified effects in the **native CAMSS/V4L2 kernel driver**: sensor CSI routing, exclusive CSID1/VFE1 PIX lease and generation, correctly sized/owned per-mode image/stats outputs, guarded per-core start/stop, source-verified interrupt and bus DMA acknowledgements, and fail-closed buffer retirement. Keep optional AE/AWB/AF/IQ decisions small, open and user-controlled through standard V4L2/libcamera controls. **Do not port** Windows Frame Server, AVStream, OEM .sys or .dll blobs, Studio Effects, AI appearance effects or the opaque Windows selector values.

The next narrowly scoped static task is now **IFE stop helper `0x221A0` → `0x27278`**, **CSID stop progress `0x21904` → `0x21B10`**, and **CDM stop-state/event `0x2854C–0x285A8`**, mapping the actually required hardware stop/IRQ/DMA lifetimes and per-core request/return structure. Decode the separate `0x809` selector and the rear-specific live profile before attempting any runtime Linux rear-ISP output. Do **not** assume these original callbacks necessarily take the same paths for front, rear, preview, photo or an application switching cameras.

## Reproduction and non-regression

`PYTHONDONTWRITEBYTECODE=1 python3 verify.py` SHA-locks the **exact original same-SP11 private ISP binary**, verifies **45 original ARM64 instruction anchors** for three initializer function-address stores, three corresponding function entries and individual `0x804/0x805` handler branches, and checks the original ARM64 PE `.pdata` function-entry metadata for all three. It exercises **14 fail-closed negative tests** rejecting false callback identities, invented active Windows routes, unproven MMIO/IRQ/DMA completion and fabricated Golden changes. `RESULT.json` contains only safe derived RVAs and conservative scalar flags, never proprietary OEM code, raw disassembly, pixel buffers, private DMA addresses or KD material. Existing protected Golden, native front PIX, IR privacy and rear RAW/software-4K fallback were not modified.
