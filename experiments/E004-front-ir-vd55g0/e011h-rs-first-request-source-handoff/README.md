# E011H — RSStats14 first request handoff

Parent Git: 2b8923849c6b38ed30fbce4207dbfa7a7106ab80 (E011G).

Status: SOURCE + LIVE REQUEST HANDOFF PASS, UPSTREAM NODE PRESET ORIGIN OPEN. Native rear ISP runtime remains denied.

The pinned original IFENode request pointer table maps entry 6 to request `+0x2C50` and entry 7 to request `+0x2CD4`. `HardcodeSettings` RVA 0x735940 has a cold/changed-family branch that copies IFENode fields `+0x9770/+0x9774` into entry 6's first two words and sets its `+0x80` flag to 1; the adjacent branch copies `+0x9778/+0x977C` to entry 7. `RSStats14` dependence function RVA 0xA0DFC0 reads the request `+0x2C50` record through context `+0xF20`. Its `AdjustROI` path and Titan680 packer were previously source-locked in E006v.

A fresh same-SP11 OEM Windows rear Color VideoRecord NV12 3840x2160 one-shot armed first RS Execute RVA 0xA0E0D0 before StartAsync. The first hit was request ID 1. Its request `+0x2C50` record began with horizontal count 16, vertical count 1024, zero offset fields and the enabled marker at record `+0x80=1`. IFENode fields `+0x9770/+0x9774` were also 16/1024, and `+0x9778/+0x977C` were zero. The request crop was inclusive 0..4063 by 0..2285 (4064x2286).

Before the first dependency, the RS module's cached configuration at `+0x60` was zero. After dependence, it held 16x1024 and derived horizontal/vertical region dimensions 254x2 from that crop, with full input extent 4064x2286. At Execute return the adjusted configuration remained 16x1024, 254x2, zero offsets and shift 5. This follows E006v's `bit_length(254*2)-4` rule and its ranges. It is a live semantic-input check, not a new raw packet byte comparison.

The source of IFENode's initial 16/1024 preset upstream of `+0x9770/+0x9774`, its mode/AFD policy and subsequent request transitions are not yet traced. Do not freeze 16/1024 or 254x2 as mode-independent native constants. The holder completed StartAsync, acquired 416 valid rear 4K handles, passed StopAsync, and ended. CDB detached; ordinary reboot returned Golden Linux with overlap guard PASS. No native rear ISP code was loaded or submitted.

Next: source-close the IFENode RS preset writer and its mode controls, then the remaining AEC_BE/AWB_BG weights/threshold transitions, BFStats25 initial AF policy, neutral 3A, LSC/GTM and VFE1 WM16 IRQ/DMA/IOMMU generation-safe retirement before native rear runtime.

Only source-safe scalar values and relationships are committed. OEM bytes, debugger logs and optical pixels stay private on SP11.
