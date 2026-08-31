# External VFE680 source comparison

Windows remains the authority. This checkpoint uses Oaklee/mainline-style CAMSS and Qualcomm's public downstream camera-driver only to classify architecture and generate the next parity hypothesis.

Oaklee's SP11 integration tree contains the upstream-style `camss-vfe-680.c`; it does not contain a hidden working Windows-like PIX/request-manager pipeline. Qualcomm's X1E-enabled downstream tree is more informative: VFE680 advertises `CAM_VFE_HW_IRQ_CAP_EXT_CSID` (SOF/Epoch0/Epoch1/EOF), while CSID680 explicitly supports AUP/RUP and exposes IPP Epoch0/1 and RUP_DONE. Its IFE manager can route request updates through CSID and forwards CSID Epoch events to the request context.

This matches the current Linux observation better than the old mental model: CSID1 already produces Epoch0/Epoch1/RUP_DONE, VFE TOP frame timing is alive, and the exact Windows RUP/AUP `CSID1 +0x18=0x01f501f5` is already submitted through RT-CDM. Therefore no duplicate RUP/AUP write follows from the public source.

The notable difference is that current Qualcomm VFE680 code does not use VFE BUS status1 bit21 for standard frame timing, RUP, completion, or BUS errors. Same-machine Windows qccamisp *does* consume `VFE BUS +0xc2c bit21` as its IFE Epoch0 lifecycle event. That makes the missing bit a likely Windows-specific lifecycle/qualification latch downstream of CSID timing, not proof that raw pixels/epochs never reach VFE.

No Linux event substitution or new MMIO write is authorized here. The next useful parity trace is same-machine Windows correlation of CSID1 IPP Epoch0/RUP_DONE against VFE1 BUS bit21 and the first BUS-retarget/replay2 consume.
