# E002h native routing audit

Read-only `media-ctl -p` on accepted E002g showed the enabled path:

- `ov13858 1-0010`:0 -> `msm_csiphy1`:0 — ENABLED, IMMUTABLE
- `msm_csiphy1`:1 -> `msm_csid0`:0 — ENABLED
- `msm_csid0`:1 -> `msm_vfe0_rdi0`:0 — ENABLED
- `msm_vfe0_rdi0`:1 -> `msm_vfe0_video0`:0 — ENABLED, IMMUTABLE
- capture node: `/dev/video0`

Active format setup while the E002g hard stream blocker remained enabled propagated:

- sensor: SGRBG10 4076x2806
- CSIPHY1 sink/source: SGRBG10 4076x2806
- CSID0 sink/source0: SGRBG10 4076x2806
- VFE0 RDI0 sink/source: SGRBG10 4076x2806
- `/dev/video0`: packed GRBG10 (`pgAA`), 4076x2806, bytesperline 5104, sizeimage 14321824

Runtime PM remained suspended and MCLK1/CSIPHY1/CSI1 timer enable counts remained zero after format configuration.
