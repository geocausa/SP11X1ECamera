# E004of — how the ISP manager obtains and uses individual core interfaces

**2026-09-24; parent E004oe, Git 334bb32f87612a1f483caa6374016598de86ee29.** This is original same-SP11 Windows OEM ISP source-locked **static** evidence only, advancing the [permanent Windows-to-native-Linux camera port map](../../../docs/CAMERA-STACK-PORT-MAP.md). It does not start any camera, inspect optical pixels, attach KD, change Linux kernel runtime or mutate protected Golden.

## A real per-core producer → consumer contract, not a generic ISP selector

The ISP manager first obtains a device-specific **bounded array of per-core records**, then calls different records for different hardware blocks. [E004oe](../e004oe-isp-manager-per-core-order-static/README.md) independently established the conditional start-like software dispatch CDM→IFE→CSID and stop-like software dispatch CSID→IFE→CDM.

E004of follows the producer side in the **same original ISP binary**:

| Original ISP step | Static source-backed instruction evidence | Important limitation |
| --- | --- | --- |
| Allocate core-indexed pointer arrays | Original caller RVA **0x69484** invokes allocator **0x3918**. The helper allocates several pointer arrays, including fields **+0x20, +0x28, +0x30, +0x38**, sized by the device-dependent hardware count. | Allocating an array does **not** mean its component or hardware is active in every capture profile. |
| Initialize manager-owned core arrays | Caller **0x69BFC** invokes **0x15768**, which initializes a bounded pool and allocates separate shared core-record arrays. | This is an original software resource allocation, not physical CSID/VFE power-up. |
| Obtain a core descriptor/interface | The original device-enumeration loop invokes helper **0x15628** at **0x697CC**, builds an individual record with **0x30-byte stride** at **0x697D0–0x697D4**, then invokes **0x15698** and **0x156E8** at **0x69818–0x69820** to obtain a hardware descriptor. | The descriptor's **specific receiving callback implementation** is not yet established. |
| Build a typed per-core record and its callable interface list | Original instructions **0x69870–0x698A8** copy status and descriptor count, store a pointer to the appropriate segment of an interface-record array at record **+0x30**, and copy each independently obtained interface pointer into a **16-byte entry**. | An exported pointer is not an export of the original OEM code itself; the actual first callback body, parameters and register effects still need separate source evidence. |
| Consume the correct record during start/stop | The same original manager accesses core-indexed arrays, checks per-core enabled/state information, loads the matching **record +0x8 callable interface**, and only then invokes the method indirectly. For example: IFE start at **0x15FAC–0x15FEC**, CSID stop at **0x16380–0x163C8**, IFE stop at **0x16408–0x16434**, CDM stop at **0x1647C–0x164B4**. | This is **conditional software dispatch**. It is not proof of completion, IRQ retirement, DMA quiescence, or a fixed recipe shared by all modes. |

The code therefore implements **specific, bounded, per-core ownership and dispatch** rather than sending one universal “camera start” to the entire chipset. Windows camera selection and profile negotiation determine which hardware blocks/records are applicable, but **which records the live rear 3840×2160 VideoRecord session used is still unknown**.

~~~mermaid
flowchart TB
 A["Selected Windows camera and capture profile"] --> B["ISP hardware manager"]
 B --> P["Original per-core descriptor enumeration"]
 P --> R["Bounded 0x30-byte core records and pointer arrays"]
 R --> C["CDM callable records"]
 R --> I["IFE callable records"]
 R --> S["CSID callable records"]
 C --> X["Concrete original receiving functions<br/>NEXT STATIC TARGET"]
 I --> X
 S --> X
 X --> H["Source-verified actual hardware effects<br/>registers, IRQ, stop and DMA retirement<br/>NOT YET PROVEN"]
~~~

## What to port to Linux and what remains unresolved

The **Linux kernel** should own exclusive CSID1/VFE1 hardware access, correct front/rear sensor routing, per-mode CSI/VFE/command resources, request generation, and lifetime of **every actual enabled DMA/statistics output**. Optional, open, user-controlled AE/AWB/AF and quality policy can live behind standard V4L2/libcamera controls. The Windows AVStream, per-GUID device-interface plumbing, Microsoft Frame Server, Device MFT, Windows Studio Effects and AI enhancements **are not required Linux runtime dependencies**.

**Do not copy a list of Windows numeric selectors or statically observed call sites into Linux.** Next trace each concrete original CDM/IFE/CSID callback body *stored in the dynamically obtained interface descriptors* and its input/output ABI. Follow the existing rear-specific VFE1 PIX evidence through real buffers, IRQ acknowledgements, independently verified stop/drain and true optical image provenance. The separate **0x809** selector, original active Windows rear profile, BF event0x0F and WM16 DMA completion, and native Linux rear hardware-ISP 4K frames remain unproven. There were no exact immediate comparison/move references to 0x809 in the examined OEM ISP binary; that negative search does **not** establish that the command is absent (it may be carried through a generic callback or jump table).

## Reproduction and non-regression

Run `PYTHONDONTWRITEBYTECODE=1 python3 verify.py`. The checker independently reads the **SHA-pinned original same-SP11 OEM ISP ARM64 binary**, verifies **56 actual original instruction anchors** for core-array allocation, individual record creation, pointer population and core-indexed consumer calls, saves only safe scalar evidence to [RESULT.json](RESULT.json), and exercises **15 fail-closed negative tests** for invalid field offsets, false live-camera/format/BF/MMIO claims and fabricated Golden mutations. Original OEM code, disassembly, optical data, DMA pointer values and KD credentials are not written to the repository.

Golden FullIO v19c, native front PIX, independent rear RAW/software-4K fallback and IR safeguards are unchanged. No camera module/firmware installed, Windows capture requested or physical device accessed.
