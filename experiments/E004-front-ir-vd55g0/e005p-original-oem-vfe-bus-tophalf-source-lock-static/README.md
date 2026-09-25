# E005p — source-lock the original OEM VFE interrupt top half before another physical run

Parent Git 897bdb0175e15e46c2f4c8943da1761da1e73fae. This stage is static only on SP11 Golden Linux. It analyzes the SHA-pinned same-SP11 original qccamisp8380.sys locally and cross-checks the already pinned Qualcomm VFE680 source from E005m. No camera stream, reboot, module load, MMIO write, KD session, BCD change or Golden mutation occurred.

## Why this stage exists

E005o materially advanced the live Windows proof: during one successful rear 4K session under external SP7 KD, every observed BF event had a non-null software FIFO8 entry and a non-null outstanding matcher. However, the two candidate BUS comp-group7 probes saw zero bit7 hits. Before another Windows/KD cycle, the actual OEM interrupt producer had to be source-locked rather than guessing another register reader.

## Exact original OEM interrupt path

The exact same-SP11 OEM driver SHA-256 is 64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c.

The full-IFE open path at RVA 0x2247c..0x2248c selects 0xc00 for the BUS window and stores VFE base + 0xc00 in the context BUS pointer. Therefore BUS-relative +0x1200/+0x1270 are VFE +0x1e00/+0x1e70, matching the independently pinned WM16 STATS_BAF geometry.

The registered top-half wrapper is RVA 0x24a30; mode0 dispatches to RVA 0x1dc20. That function snapshots four raw 32-bit words before the DPC:

- TOP status0: VFE +0x44
- TOP status1: VFE +0x48
- BUS status0: BUS +0x28 = VFE +0xc28
- BUS status1: BUS +0x2c = VFE +0xc2c

The DPC at RVA 0x24a70 retains those raw words separately. Its auxiliary normalized mask is used for interrupt coalescing/timing and must not be silently reinterpreted as the hardware composite-group bitmap.

## BF event source correction

The OEM BF software event is not directly generated from BUS status0 bit7.

Mode0 event dispatch RVA 0x1ef90 receives the raw packet. RVA 0x1eff0 loads TOP status0/status1; RVA 0x1f048 extracts TOP status1 bit7, and RVA 0x1f190 emits event ID 0x0f. The existing source-locked event branch then pops software FIFO group8 and uses BF resource port 0x300d.

Therefore E005o's positive BF/FIFO8/matcher chain and its negative candidate BUS7 observations are not contradictory. They were observing different interrupt domains.

## OEM BUS writeback divergence

After snapshotting BUS status0/status1 from VFE 0xc28/0xc2c, the exact OEM top half writes those captured values to BUS-relative +0x3c/+0x40 (VFE 0xc3c/0xc40) and then writes 1 to BUS-relative +0x30 (VFE 0xc30).

A bounded whole-image direct-access scan of registers loaded from context +0x150 found BUS mask writes at +0x18/+0x1c, BUS status reads at +0x28/+0x2c, global write at +0x30, the status-mirroring write pair at +0x3c/+0x40, and zero direct stores to +0x20/+0x24 through that context pointer.

This remains a conservative finding. It does not prove the OEM can never reach c20/c24 through an aliased or indirect path.

The pinned Qualcomm VFE680 reference independently defines BUS clear0/clear1 = 0xc20/0xc24, BUS status0/status1 = 0xc28/0xc2c, BUS global clear = 0xc30, and 0xc3c/0xc40 as IF frame-header configuration entries.

So the OEM c3c/c40 writeback sequence is an unresolved divergence. Do not copy that write sequence into Linux. E005n's canonical Qualcomm-style observer remains unloaded.

## What is proven now

The actual OEM full-IFE interrupt top-half and DPC chain is source-locked; the OEM snapshots raw TOP0/TOP1/BUS0/BUS1; its BUS status reads are VFE c28/c2c; BF event 0x0f is sourced from raw TOP status1 bit7 rather than directly from BUS status0 bit7; WM16 remains independently source-locked as STATS_BAF at VFE 1e00/1e70; and the pinned Qualcomm reference assigns WM16 to composite group7.

## Still not proven

The original Windows runtime configuration packet carries a per-output Composite Group id field, but the actual live BF/resource 0x300d value has not yet been captured. Nor does this static stage prove that one live FIFO8 object is the same generation/buffer independently completed by WM16, or establish trusted DMA/IOMMU quiescence and safe reuse.

Native rear processed ISP therefore remains DENIED.

## Next smallest experiment

A new bounded Windows run should use SP7 as the external KD host and auto-continue logging at the already source-locked OEM top half. Capture the complete raw TOP0/TOP1/BUS0/BUS1 tuple before writeback for interrupts where TOP1 bit7 produces BF, and capture or derive the live composite-group scalar for resource 0x300d. Correlate that with the already proven FIFO8 non-null/matcher chain and WM16 consumed-address state. Do not load E005n merely because this static stage exists.

Run: PYTHONDONTWRITEBYTECODE=1 python3 verify.py
