# E005x — source-lock VFE680 external-CSID WM16 buffer-done and consumed-address fence

Parent Git `c4f9a98c`.

This stage is static only on protected Golden Linux. It uses the pinned Qualcomm camera-driver v1.0.6 source already accepted for the SP11 VFE680 generation plus the SHA-pinned same-SP11 Windows `qccamisp8380.sys` facts proven in E005m–E005w. No camera stream, reboot, module load, MMIO write or debugger session occurs.

## Result

The missing physical-completion architecture is now source-locked end to end for the VFE680 generation.

### 1. VFE680 buffer-done is external to VFE and delivered through CSID

`cam_vfe680_hw_info` advertises `CAM_VFE_HW_IRQ_CAP_EXT_CSID`, not a local VFE buffer-done IRQ.

BUS-v3 explicitly handles this case: when local `CAM_VFE_HW_IRQ_CAP_BUF_DONE` is absent, acquire copies the hardware-manager supplied `buf_done_controller` into BUS common data. The IFE hardware manager obtains that controller from CSID and passes it to VFE acquire.

CSID680 defines that controller on:

- BUF_DONE status `0x8C`
- BUF_DONE mask `0x90`
- BUF_DONE clear `0x94`
- BUF_DONE set `0x98`

The generic CSID handler delegates this interrupt to the CSID `buf_done_irq_controller`.

These are the exact status/clear offsets independently observed in the same-SP11 Windows type-1 BF path: Windows reads `+0x8C`, preserves bit7 in the live zero-format path, and ACKs by writing the saved status word to `+0x94`.

### 2. WM16 / STATS_BAF owns completion group 7 = BIT(7)

The VFE680 BUS-client descriptor identifies client16 as STATS_BAF / WM16:

- CFG `0x1E00`
- ADDR_STATUS0 `0x1E70`
- `comp_group = CAM_VFE_BUS_VER3_COMP_GRP_7`

VFE680 has 17 completion groups and defines `comp_done_mask[index] = BIT(index)`, therefore group7 is exactly `BIT(7)`.

The VFE680 output table maps `CAM_VFE_BUS_VER3_VFE_OUT_STATS_BF` to WM index16.

BUS-v3 derives each output's completion mask from the WM hardware descriptor, places that mask in the buffer-done IRQ subscription, and subscribes the output to the external `buf_done_controller`.

Therefore for VFE680 STATS_BF/WM16 the physical buffer-done predicate is the CSID BUF_DONE controller's status bit7.

### 3. The completion handler reads WM16 last-consumed address on that event

On a subscribed output-done event, BUS-v3 tests `status_0 & resource_data->comp_done_mask`. When true it reads the output WM's `addr_status_0` into `evt_payload->last_consumed_addr`.

The bottom half separately verifies the same composite completion mask, converts it into `CAM_ISP_HW_EVENT_DONE`, and emits:

- output resource id
- completion-group id
- `last_consumed_addr`

For WM16 this is group7 / BIT7 and address register `0x1E70`.

### 4. VFE680 requires consumed-address identity before successful retirement

VFE680 sets `support_consumed_addr = true`. That capability propagates through the IFE hardware manager into the ISP context.

The ISP context's activated-state BUF_DONE path therefore uses address verification. It compares:

`done->last_consumed_addr`

against the request's mapped output address:

`fence_map_out[i].image_buf_addr[0]`

(with the platform's 36-bit IOVA normalization when applicable).

If the resource/address pair does not match the current request, it is not accepted as that request's completed buffer; the code can search another resource in the same completion group or defer/re-associate a delayed IRQ.

Only after a valid completion association does the success path release the SMMU buffer-tracker reference and signal the output sync fence `CAM_SYNC_STATE_SIGNALED_SUCCESS`.

This is the reference generation's DMA/IOMMU lifetime contract: hardware completion bit plus exact last-consumed IOVA identity gates successful ownership return.

## Windows convergence

The previously accepted same-SP11 Windows evidence now lines up with that architecture without inventing a numeric namespace translation:

- OEM resource `0x300D` source-locks to WM16/STATS_BAF (`VFE+0x1E00`).
- The live Windows zero-format type-1 path reads CSID BUF_DONE `+0x8C`, tests bit7 to emit BF event `0x0F`, and ACKs the saved word at `+0x94`.
- BF processing pops FIFO8, synchronously reads WM16 `ADDR_STATUS0` (`VFE+0x1E70`) and CFG0, then key/tag-matches the CSID current-SOF timestamp token.
- Live E005o/E005s proved the BF/FIFO8/matcher chain repeatedly under rear4K.

The important correction is that CSID bit7 is not merely an arbitrary BF-correlated status bit on this hardware generation. The pinned VFE680 architecture uses the external CSID BUF_DONE controller as the VFE BUS completion source, and WM16's completion mask there is BIT7.

This closes the static physical WM16 completion predicate and reference retirement semantics.

## What this does and does not authorize

This result removes the need for another blind Windows IFE-top-half discriminator run. E005w's silent candidate top-half probes are orthogonal to the external-CSID buffer-done architecture.

It also means Linux should not invent a FIFO-key-to-DMA-address equivalence. The robust implementation model is the VFE680 model itself:

1. observe CSID BUF_DONE BIT7;
2. read WM16 ADDR_STATUS0;
3. match that consumed IOVA against Linux's actually queued WM16/statistics buffer;
4. only then retire/requeue that exact buffer;
5. ACK through the canonical CSID BUF_DONE clear path.

Native rear processed ISP remains **DENIED** until that contract is implemented and validated on Linux. The reverse-engineering gate for the WM16 completion predicate/lifetime model is now closed; the next gate is implementation/runtime validation, not more Windows provenance hunting.

## Next

Move back to the isolated Linux VFE680 observer/candidate lineage. Review E005n against this newly source-locked external-CSID architecture. Build a fresh candidate that observes CSID BUF_DONE BIT7 + WM16 ADDR_STATUS0 and correlates only against Linux-owned queued buffer IOVAs before any retirement action. First runtime should remain observer-only; retirement/requeue is enabled only after exact-address correlation is demonstrated.
