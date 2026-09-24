# E004od — trace the Windows ISP hardware-manager callback underneath AVStream

**2026-09-24; parent E004oc, commit c583437a310297d546e1150da5b6147e253db310.** Same-SP11 original OEM ARM64 AVStream and Qualcomm ISP drivers were examined **read-only**, no Windows camera session or physical Linux device interaction. This addresses the user’s question of whether an OEM camera orchestrator chooses the correct native commands, and pins the specific Windows request-to-hardware *software* boundaries that should guide the clean Linux L0–L3 port. This is a **static source-checked call chain**, not proof that any particular 4K session took every branch.

## The formerly unknown second ISP callback is now identified

<code>CCameraEngine</code> does **not** directly write a VFE register in its OnStart/OnStop handler. Following the source-verified, per-GUID routing of E004oc, the engine’s conditional alternate interface dispatch at AVStream RVA <code>0x20DA8</code> passes a selector into the ISP driver’s first callback at ISP RVA <code>0x4E30</code>. The ISP callback passes selectors such as <code>0x804</code> and <code>0x805</code> onward to an interface stored in the ISP device context at offset <code>+0x10</code> (RVA <code>0x51E0</code>).

**E004od traces the producer of that second interface rather than guessing it.** An ISP device-initialization function beginning near RVA <code>0x6A0A0</code> obtains the relevant typed device context (RVA <code>0x6A13C–0x6A164</code>) and passes its <code>+0x10</code> output field to a helper at ISP RVA <code>0x15A40</code> (call RVA <code>0x6A2F4</code>). The helper searches a bounded **16-entry pool, record stride <code>0xE38</code>**, marks an available record and stores a pointer to that record’s interface field at record offset <code>+0x48</code> in the context output. On success it writes the **actual callback function pointer to ISP RVA <code>0x15D70</code>** into that interface’s first slot (RVA <code>0x15B70–0x15B80</code>).

Consequently, the original chain is:

~~~mermaid
flowchart TD
 A["AVStream camera engine\nOnStart / OnStop"] --> B["Engine backend GUID-selected interface\nconditional alternate callback"]
 B --> C["ISP outer callback\nRVA 0x4E30"]
 C --> D["ISP typed device context +0x10\n16-record bounded pool"]
 D --> E["ISP hardware-manager callback\nRVA 0x15D70"]
 E --> F["Selector 0x804\nconditional start-like per-core fan-out"]
 E --> G["Selector 0x805\nconditional stop-like per-core fan-out"]
 F --> H["Lower per-core callable interfaces\nimplementation and physical register effects not yet mapped"]
 G --> H
~~~

The original ISP contains diagnostics describing **ISP HW Manager / IFE / CSID / CDM start and stop**, consistent with this code’s per-core control design, but this evidence **does not identify each indirect per-core callback implementation, prove a specific CSID/VFE register sequence or establish which backend actually ran in a Windows rear VideoRecord session**.

## Separate start-like and stop-like branches

At ISP callback RVA <code>0x15D70</code>, the original source receives the numeric selector in <code>w1</code>. **Selector <code>0x804</code>** selects branch RVA <code>0x15EE0</code>, tests current owner/initialized state, and on eligible paths calls multiple **distinct core-interface arrays with selector <code>0x804</code>** (examples: RVA <code>0x15F3C–0x15F50</code>, <code>0x15FD8–0x15FEC</code>, <code>0x161EC–0x16208</code>). It tests returns and contains failure/rollback paths.

**Selector <code>0x805</code>** selects a different branch at RVA <code>0x16300</code>; it clears a session-state flag and invokes per-core interfaces with <code>0x805</code> (examples: <code>0x163AC–0x163C8</code>, <code>0x16414–0x16434</code>, <code>0x164A0–0x164B4</code>) with conditional error handling, then iterates over the active core set. These are **conditional code paths**, not a promise of the same number of callbacks in every camera profile or a verified physical stop order. **<code>0x809</code> has NOT been decoded by this experiment.**

**Native Linux consequence:** kernel CAMSS/CCI must implement *the demonstrated hardware safety outcomes* independently: validated per-sensor power/mode, exclusive CSID1/VFE1 owner, per-mode ISP configuration, all enabled DMA/statistics ownership, verified stop/drain and no stale IRQ or buffer free. We must trace the per-core callbacks and hardware registers before installing any experimental rear ISP driver. Optional user-controllable 3A/image controls may live in a small open libcamera IPA. The Windows device-interface acquisition, numeric selectors, client Frame Server and AI/Studio Effects should not be copied into Linux.

## Verification and precise remaining gap

[verify.py](verify.py) SHA-locks the exact private same-SP11 original AVStream and ISP images, checks **50 independent original ARM64 instruction anchors** across the outer ISP callback, device-context initialization, pool allocator, actual installed nested callback and two different per-core fan-out branches. Its sole export, [RESULT.json](RESULT.json), contains safe derived RVAs, bounded pool dimensions and explicit statements that live rear profile/backend selection, <code>0x809</code>, per-core receiving functions, BF/WM16 completion and Linux-native rear processed 4K **remain unproven**. It also runs **16 fail-closed negative mutations** against false callback names, pool dimensions, invented hardware/protocol semantics and fabricated successful capture. No OEM code, raw disassembly, firmware, KD credential, DMA address or optical frame is exported.

**Next specific static task:** trace the three original ISP hardware-manager per-core interface arrays and the receiving **IFE, CSID and CDM callback implementations**, map the 0x804 and 0x805 request arguments to independently observed clocks, CSI routing, ISP output allocation, IRQ/drain and safe shutdown, and treat 0x809 separately. A bounded real Windows session *after* the source-based map may then verify which of those routes rear VideoRecord/preview/still/switch actually use. Previous E004nv BF event-0x0F is **mode-specific static evidence**, not live completion, and Linux rear native processed-4K optical frames are still **unproven**. Golden FullIO v19c, front native PIX and rear RAW/software-4K fallback remain untouched.
