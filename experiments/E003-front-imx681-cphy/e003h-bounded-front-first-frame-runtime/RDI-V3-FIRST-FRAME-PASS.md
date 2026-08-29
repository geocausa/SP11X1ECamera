# E003h bounded front RDI first-frame PASS

Date: 2026-08-29

This is a **physical transport diagnostic**, not Windows VFE1 PIX/ISP parity.

The disposable V3 boot used the front-only C-PHY graph, Golden initrd, and
`modprobe.blacklist=qcom_camss,imx681,ov13858`. After userspace was fully up,
only the generic media dependencies plus the exact candidate qcom-camss and
IMX681 modules were loaded manually.

Accepted path:

`IMX681 3840x2640 SRGGB10 -> CSIPHY2 one-trio C-PHY -> CSID1 RDI0 -> VFE1 RDI0 -> /dev/video4`

Negotiated V4L2 output:

- `V4L2_PIX_FMT_SRGGB10P` / fourcc `pRAA`;
- 3840x2640;
- 4800 bytes/line;
- 12,672,000 bytes/frame.

One bounded `VIDIOC_STREAMON` succeeded. Sequence 0 dequeued 12,672,000 bytes,
then normal STREAMOFF caused the sensor to write MODE_SELECT=0 and runtime
power off. The captured packed RAW10 is SHA-256
`8e892cfeb8f9aea6c9454dbc1fe22b0c26a11e4a108e551a2995069d76e000ac`.

RAW10 validation after unpacking:

- zero fraction: 0;
- min/max: 60 / 478;
- mean: 64.417539;
- standard deviation: 2.261782;
- 295 unique 10-bit values;
- Bayer means R/G1/G2/B = 64.359 / 64.542 / 64.513 / 64.256;
- the percentile-mapped preview visibly resolves the room/window scene, proving
  this is image content rather than a repeated DMA pattern.

The raw frame, unpacked frame and preview remain **local/untracked**. Only their
hashes/statistics and filtered camera logs are recorded in Git.

Teardown PASS:

- IMX681 runtime PM: suspended;
- CAMSS runtime PM: suspended;
- mutable CSIPHY2->CSID1 and CSID1->VFE1-RDI0 links disabled;
- `cam_cc_mclk4`, `cam_cc_csiphy2`, `cam_cc_csid`, `cam_cc_ife_1` and related
  camera clock prepare/enable counts are zero;
- camera regulator use counts are zero;
- no BUG/Oops/panic/SError was observed.

Golden remained the saved GRUB default throughout. RT-CDM FIFO0 and VFE1 PIX
were not used by this RDI diagnostic.
