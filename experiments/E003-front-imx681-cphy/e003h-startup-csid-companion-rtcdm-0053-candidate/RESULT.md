# E003h 0053 result — startup CSID companion RT-CDM transport

The one authorized 0053 differential executed exactly once and returned immediately to FullIO v19c Golden. No same-boot retry occurred and no QC10C output was produced.

0053 moved the four already-proven startup CSID1 descriptor-1 companion command lists from Linux CPU MMIO replay to the exact captured Windows RT-CDM ownership: `CHANGE_BASE(CSID1)` followed by the exact companion BL. No register value, crop coordinate, RUP/AUP value, VFE, CSIPHY, sensor or DT programming changed.

The transport correction definitely executed: RT-CDM completed FIFO sequence **25**, versus **17** in consumed 0052, exactly the expected +8 submissions (CSID CHANGE_BASE + companion BL for four startup packets), with `faulted=0`.

The camera failure is unchanged. The first four IPP status/geometry samples remain `00811dd0/00000f00 -> 00600cc0/00000f00 -> 00000cc0/00000f00 -> 00004ee8/0a500f00`. Completed EOF is still 3840x2640 with `ERROR_LINE_COUNT`; HBI remains the Windows-matching `0x03b203ad`; VFE1 raw Epoch0 remains absent; QC10C remains absent. Crop/readback remains `0x0eff0000/0x086f0000` with expected frame `0x08700f00`.

Therefore the Windows/Linux startup companion **transport ownership mismatch was real but is not causal for the vertical-crop failure**. Retire it as a crop hypothesis. Runtime is blocked again until a new concrete static delta is proven.
