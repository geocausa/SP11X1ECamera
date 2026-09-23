# E004nk — rear VFE0 PIX source-only preflight

Date: 2026-09-23. This is a **source-only** boundary check, not a live native rear ISP capture or a Windows driver port. It reads the already-accepted local, scalar-only E003i IG/HY/Z and E004lr records and decodes a tracked accepted unified DTB with `fdtget`; no sensor, boot, kernel module, firmware, Windows partition, frame buffer, optical image, photo hash or private hardware input is accessed.

## Newly pinned distinction

- **Front (proven bounded native VFE PIX):** IMX681 C-PHY `msm_csiphy2 -> msm_csid1 -> msm_vfe1_pix -> msm_vfe1_video3`, front Bayer SRGGB10 3840x2160; HY 27 genuine QC10C frames and Z six paired native 3A generations.
- **Rear (proven RAW/RDI, not PIX):** OV13858 D-PHY `msm_csiphy1 -> msm_csid0 -> msm_vfe0_rdi0 -> msm_vfe0_video0`, rear Bayer SGRBG10 4076x2806 (E004lr). Its DT endpoint pair is bidirectional and the rear sensor's four physical D-PHY lanes 1..4 correspond to CAMSS lane indices 0..3. These *numbers and bus types must not be copied from the front*.
- **Design target, unproven:** Archived IG media inventory shows `msm_csid0` pad4 -> `msm_vfe0_pix` -> `msm_vfe0_video3` (archived `/dev/video3`), but none of these are an enabled and validated rear PIX stream. The native write-master/SMMU mapping, RT-CDM/IQ generation, format, crop and buffer layout still require exact source/hardware evidence. The actual full-sensor 4076x2806 RAW mode is not the same claim as 3840x2160 processed video. QC10C is **proven for front only**, and is not yet a verified rear output format or a Windows-equivalent RGB image.
- SAME-SP11 Windows rear OEM package is MSHW0491 OV13858 and selected tuning `com.surface.tuned.rfc_ov13858.bin` (E004ni); MSHW0561 and front IMX681 tables do not qualify as rear tuning.
- Windows Xtensa ICP images cannot be launched through the Linux ADSP/CDSP remoteprocs (E004nj). No firmware or Windows binary was loaded.

## Exact source-level blockers confirmed on this SP11

The archived IG media topology exposes `msm_vfe0_pix` and a video3 entity, so the *entity's existence* is not the missing feature. The currently checked local CAMSS source is the blocker:

1. `/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss/camss-csid-680.c`, function `__csid_sp11_front_ipp_mode0`, explicitly requires `csid->id == 1`, `csiphy_id == 2`, `CSID_PHY_SEL_CPHY`, one lane, `MEDIA_BUS_FMT_SRGGB10_1X10`, width 3840 and height 2160. Companion, enable, epoch, interrupt and stop handling all hinge on this front-only predicate; a rear route cannot use it unmodified.
2. The same local kernel's `camss-vfe-680.c` function `vfe680_x1e_bus_target` requires `vfe->id == 1`; the verified front FULL write-master/client contract is thus not a validated VFE0 rear output contract.
3. The rear Windows MSHW0491 sensor tuning and active video/still ISP parameter ownership have not yet been mapped into an independently derived rear-specific IQ/RT-CDM command sequence, and neither VFE0 PIX output format nor SMMU/geometry/clock contracts are proven. Disabling the front-only predicates or replaying their register values would bypass these essential checks, not constitute a safe port.

**Engineering outcome:** implement a **separate, fail-closed rear-mode guard** for the validated OV13858 CSID0+D-PHY+GRBG geometry first; derive rear-specific IPP epoch/crop, VFE0 FULL client and native IQ/control/buffer ownership separately before enabling any physical rear PIX one-shot. The original front guard and Golden boot remain unchanged. Archived `/dev/video3` numbering is not a stable node identity across candidate boots; rediscover video entity and media links at runtime.

## Reproducible camera-free check

```sh
python3 experiments/E004-front-ir-vd55g0/e004nk-rear-vfe0-pix-source-preflight/preflight.py
python3 experiments/E004-front-ir-vd55g0/e004nk-rear-vfe0-pix-source-preflight/test_preflight.py
```

The checker *fails closed* on front/rear route swaps, RAW format/Bayer swaps, wrong D-PHY/C-PHY types, non-reciprocal DT graph links and lost original front proof. Its result is **not** a permission to arm a candidate.

## Next engineering gate

Inspect the exact accepted CAMSS VFE0 PIX/IPPs/RT-CDM and OV13858 link/crop source, then derive a rear-only independent host IQ command contract from SAME-SP11 OEM rear behaviour. Only when the rear VFE0 PIX buffer/video geometry, selected rear tune ownership, SMMU/bandwidth and deterministic cleanup are source-locked should a *fresh* unique single-use, opt-in, Golden-return physical first-frame attempt be prepared. Preserve E004ne software fallback, never rearm consumed E003i/E004 candidates, keep IR off and never initiate Linux OS suspend.
