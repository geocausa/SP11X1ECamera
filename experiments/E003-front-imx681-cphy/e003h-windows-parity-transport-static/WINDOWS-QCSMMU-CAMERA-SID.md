# E003h same-machine Windows qcsmmu camera SID oracle

Date: 2026-08-30

This checkpoint uses the exact installed same-machine Windows `qcsmmu8380.inf` as static hardware-routing evidence. The INF itself is not committed.

Exact local source identity: 53,052 bytes, SHA-256 `c1afd89419c12ca093a7d3b1f80ef980723d78d3549ceb158b9ee1a1ca051846`, driver version `1.0.4160.6000`. The fail-closed extractor `extract_qcsmmu_camera_sid.py` regenerates `windows-qcsmmu-camera-sid-oracle.json`.

The SMMU0 context table assigns VFE client `0x01` to CB16/VM4 **S1_IFE_HLOS** and CB17/VM4 **S1_ICP_IPE_BPS_CDM**. The corresponding same-machine S2CB maps are:

- CB16 S1_IFE_HLOS: SID `0x0800` mask `0x0060`; SID `0x18a0` mask `0x0000`.
- CB17 S1_ICP_IPE_BPS_CDM: SID `0x1800` mask `0x0060`; SID `0x1900` mask `0x0000`; SID `0x1980` mask `0x0020`.

This proves that `0x18a0` is a real same-machine Windows VFE/IFE HLOS SMMU route. It does **not** by itself prove that RT-CDM1 command fetches specifically emit SID `0x18a0`; that narrower requester identity remains a separate provenance question.

A public X1E80100 CAMSS v13 binding patch independently labels the five CAMSS S1 HLOS streams as IFE/IFE_LITE read+write, SFE read+write and **CDM IFE**, and changes the example to `0x800/0x60`, `0x820/0x60`, `0x840/0x60`, `0x860/0x60`, `0x18a0/0`. This public Linux material is corroboration/implementation guidance only, not Windows proof: https://patchew.org/linux/20260728-b4-linux-next-25-03-13-dtsi-x1e80100-camss-v13-0-ae811e2f0799@linaro.org/20260728-b4-linux-next-25-03-13-dtsi-x1e80100-camss-v13-4-ae811e2f0799@linaro.org/

The currently integrated Linux camera infrastructure still carries the older eight-entry IOMMU list and omits `0x18a0`. Therefore the present Linux CAMSS DMA-domain setup cannot be accepted as a proven RT-CDM command-fetch mapping. Runtime remains blocked.
