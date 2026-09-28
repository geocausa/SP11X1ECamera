# E011M — RSStats14 Titan680 preset origin

Parent Git: 4ce09467d18a230f06a93349320b47dbe6879ef8 (E011I).

Status: **SOURCE + LIVE FIRST-WRITER CLOSED for the active Titan680 rear path.** Native rear ISP runtime remains denied.

E011H established that request 1 consumes RS counts 16/1024 from IFENode `+0x9770/+0x9774`, but the producer of those IFENode fields was still open. Fresh same-SP11 tracing now reaches earlier than that handoff.

A constructor-entry trace on the newly created IFENode observed `+0x9764..+0x977C` all zero. An exact process-scoped 8-byte write watch was then armed on that same object's `+0x9770`. The **first write** hit stable QcDeviceMFT8380.dll RVA `0x8A2158`, inside function RVA `0x8A2150`. Immediately before the store, the watched pair was 0/0; the store value was `0x0000040000000010`, and a single step changed the pair to 16/1024. The caller return address was RVA `0x74EDC8`, inside the pinned `CamX::IFENode::ConfigureIFECapability` function.

Pinned static decompilation makes the writer exact. RVA `0x8A2150` receives the destination at IFENode `+0x9764` and writes the following five 32-bit words in one literal capability/default-statistics block:

- `+0x9764 = 18`
- `+0x9768 = 14`
- `+0x976C = 14`
- `+0x9770 = 16`
- `+0x9774 = 1024`

The adjacent `+0x9778/+0x977C` pair is not written by this function and remained zero in the live first-writer trace.

The source chain identifies the owning hardware pipeline without inventing a method name. `ConfigureIFECapability` constructs the Titan680 IFE pipeline through RVA `0x8A35A0`; that constructor installs vtable `0x133E568`. Vtable slot `+0x80` (entry `0x133E5E8`) points to RVA `0x8A2150`, and `ConfigureIFECapability` invokes that slot with IFENode `+0x9764` as the destination. Nearby source strings and methods identify the object as `CamX::IFEPipelineTitan680`. The exact C++ name of this virtual `+0x80` method is not recovered, so this checkpoint names it only as the **Titan680 pipeline capability/default-statistics writer**.

A separate fresh E011L trace had already shown 16/1024 present at entry to `CamX::IFENode::ReadDefaultStatsConfig`, proving that function and its downstream default-statistics helper are consumers, not the origin. E011M closes the remaining interval: IFENode starts at zero and the Titan680 capability virtual writes 16/1024 during `ConfigureIFECapability`, before `ReadDefaultStatsConfig` and long before E011H's `HardcodeSettings` request copy.

This closes the **initial active-Titan680 RS preset origin**. It does not establish that 16/1024 is universal across other Titan generations or that later request/mode overrides cannot occur. Native rear ISP remains denied by the other E008p semantic bootstrap gates and the independent VFE1 WM16 IRQ/DMA/IOMMU same-generation retirement/lifecycle proof.

The E011M rear4K holder completed StartAsync and StopAsync with 1,593 valid 4K handles. Breakpoints were cleared before an ordinary reboot. SP11 returned to protected Golden Linux kernel `7.1.5-sp11-render-parity-v4+`, saved GRUB entry `sp11-audio-fullio-v19c`, empty `next_entry`, with no camera modules or camera nodes present. No native rear ISP module was installed, loaded or submitted.

Only source-safe scalar relationships and stable RVAs are committed. OEM bytes, debugger logs, process addresses and optical payloads remain private on SP11.

Next: resume the remaining E008p first-frame semantic bootstrap audit (AEC_BE/AWB_BG transitions, BFStats25 initial AF policy, neutral 3A, LSC/GTM), while separately closing VFE1 WM16 same-generation IRQ/DMA/IOMMU retirement and lifecycle serialization before any native rear ISP runtime.
