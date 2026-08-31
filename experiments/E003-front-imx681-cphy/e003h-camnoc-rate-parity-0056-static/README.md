# E003h 0056 static — X1E front IFE1 CAMNOC RT 300 MHz parity

0055 directly measured a same-machine clock-rate mismatch at the CAM_CC hardware boundary: stock Windows front-camera streaming uses CAMNOC RT `CFG=0x00000203` / branch enabled, which is 300 MHz; Linux enables the same branch but leaves `CFG=0x00000000`, i.e. the 19.2 MHz BI_TCXO/default source.

0056 is the smallest bounded correction. Inside the already-private E003h X1E front one-shot runner, after `v4l2_pipeline_pm_get()` powers IFE1 and before PIX allocation/RT-CDM/startup, it finds IFE1's existing `camnoc_rt_axi` CCF handle, requires `clk_round_rate(..., 300000000)` to return exactly 300 MHz, then calls `clk_set_rate()` once. The helper rejects non-X1E80100, non-IFE1, missing-clock or rounded-rate mismatch cases.

There are no new direct MMIO reads/writes, sensor writes, CSID values, VFE values, RT-CDM command changes, DT changes, or sensor changes. Strict checkpatch is 0/0/0 and the module has exact Golden vermagic. The patch reverses exactly to the frozen 0054/0055 CAMSS source.

Static inspection: `0056-static-inspection.json`. Runtime is **not authorized** at this checkpoint.
