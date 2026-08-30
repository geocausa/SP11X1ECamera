# E003h replacement post-provenance PIX runtime result — 2026-08-30

The single replacement candidate boot and the single authorized root helper invocation were consumed. No same-boot retry occurred. The wrapper archived the result and rebooted immediately to Golden.

## Result

The run advanced materially beyond both earlier diagnostics but did **not** produce a QC10C frame. The userspace helper returned `ETIMEDOUT` after about 0.80 seconds.

Mechanically observed progress:

- CAMSS attached to the translated SMMU domain with the corrected five-entry fwspec including Windows-proven requester SID `0x18a0`.
- RT-CDM reset completed and the engine progressed through the full pre-CSID command prefix.
- Persistent stage telemetry reached `fifo_seq=13`, `stage=fifo-done`, with FIFO0 BL-done `last_status=0x4`, no FIFO1/2/3 status and no RT-CDM fault.
- The 13 completed FIFO commits correspond to startup0 + complete prime0 + startup1 + complete prime1 + startup2 + startup3. The last completed command is startup packet3 (`len=0x4e7` encoded low-20 length).
- CSID1/CSIPHY2/sensor start proceeded far enough for IMX681 to log `MODE_SELECT=1 front transmission started`.
- No post-sensor prime2 was submitted: the runner next waits for VFE1 raw Epoch0 before BUS slot1 retarget and prime2.
- The wait for VFE1 Epoch0 timed out; teardown then stopped sensor transmission, masked/stopped RT-CDM, and returned sensor/CAMSS runtime PM to suspended.
- No QC10C output file exists.
- Golden return is clean: protected FullIO v19c boot, saved/default Golden, empty `next_entry`, no candidate camera module loaded.

## Consequence

This run closes the previous RT-CDM/SMMU uncertainty for the bounded path: Linux command-buffer DMA is visible to RT-CDM1 and the complete pre-CSID startup/priming prefix executes with BL-done completions. The current failure is **after sensor-on and before Epoch0**, not an RT-CDM reset/FIFO timeout.

The runner currently omits the separately proven Windows host stage `IFE resource start` that appears between RT-CDM start and startup packet0 in the retained `0022` contract. `v4l2_pipeline_pm_get()` provides resource power but is not itself the Windows `IFE start command 0x804` operation. Before any further runtime, statically recover/represent the exact Windows IFE resource-start semantics and prove whether that missing stage is required to generate the VFE1 Epoch0 event. Do not authorize another PIX run until that is closed and inspected.
