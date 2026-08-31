# E003h 0054 runtime result — sensor/CSID geometry fixed; VFE1 Epoch0 still absent

The single authorized 0054 run executed once and returned immediately to FullIO Golden. There was no retry. IMX681 and CAMSS are suspended after the run, `saved_entry` is Golden, `next_entry` is empty and no camera module remains loaded.

## Decisive result

The Windows-selected IMX681 resolution record 2 was programmed successfully and transmission started at 3840x2160@30. This fixes the previous Linux CSID1 completed-frame fault exactly:

- 0053 first completed sample: `0x00004ee8 / 0x0a500f00` = 3840x2640 with `ERROR_LINE_COUNT` bit14.
- 0054 first completed sample: `0x00000ee8 / 0x08700f00` = 3840x2160 with no bit14.
- subsequent retained 0054 frame samples remain 3840x2160.
- `ipp-history` contains no bit14 and the line-error snapshot is all zero.
- CSID RX reports no ECC or CRC error.

Therefore the prior Linux sensor-mode mismatch was **causal for the CSID line-count/geometry failure**.

It was **not causal for the VFE1 stall**. VFE1 still reaches the same raw Epoch0 timeout boundary and no QC10C output is produced. RT-CDM completes FIFO sequence 25 without a fault, matching 0053 transport behavior.

The remaining failure boundary is now strictly downstream of healthy CSID1 frame reception: **after CSID1 receives/measures valid 3840x2160 frames and before VFE1 raw Epoch0 / FULL output**.

The Windows first-IPP raw log remains missing; its reported sequence is preserved only as a provenance note and is not substituted/reconstructed. Exact bounded Windows evidence does independently show completed CSID geometry 3840x2160 with bit14 absent, which Linux 0054 now matches.

Runtime analysis: `runtime-0054-analysis.json`, SHA-256 `a77d1ec6876710ce3d885dcdf3063969558643555b72534f09cef11d6ffd7d6e`.

**0054 authorization is consumed. No further 0054 runtime is permitted.** Next gate is downstream Windows/Linux VFE1/IFE startup-state analysis; no new hardware candidate until a concrete delta is proven.
