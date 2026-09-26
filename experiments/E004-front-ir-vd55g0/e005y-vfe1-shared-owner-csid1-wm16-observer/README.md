# E005y — shared VFE1 owner + correct CSID1/WM16 observer (build-only)

Parent Git: `77d39e06` (E005x).

E005x closed the static VFE680 completion model: WM16/STATS_BAF completion is delivered through external CSID BUF_DONE bit7 and VFE680 requires the corresponding last-consumed IOVA to match the queued output before ownership is returned.

E005y moves that proof into a fresh isolated Linux CAMSS candidate without enabling native rear ISP.

## Design

- Introduce one per-CAMSS shared VFE1 owner with mutually exclusive FRONT/REAR identity and monotonic epochs.
- Scope the already-proven custom front runner under FRONT ownership before any power/start and release it only after its existing safe teardown. A failed teardown permanently pins ownership until reboot.
- Keep generic X1E VFE1 PIX streaming denied by the existing `vfe_enable_v2()` gate.
- Add a read-only VFE680 helper for VFE1 WM16 `ADDR_STATUS0`.
- In the existing CSID680 ISR, consume the already-latched BUF_DONE word after its existing single clear/ACK. For CSID1 bit7:
  - front ownership may record only a front-scoped status observation;
  - WM16 is read only if a current REAR owner epoch and the exact source-proven rear CSID1 route predicate are both valid;
  - the owner epoch is rechecked after the MMIO sample so a concurrent handoff cannot misattribute it.
- No `camss_buf_done`, VB2 completion, DMA unmap/free, requeue, IRQ-mask mutation, second ACK, rear hardware start or retirement is introduced.
- Rear runtime authorization remains `-EOPNOTSUPP` in this stage.

The build is intentionally isolated and is not installed or loaded.
