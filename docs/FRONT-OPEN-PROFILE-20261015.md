# Front camera: open ISP start-up profile replaces the private one (2026-10-15)

Upstreaming step 1 for the front camera (imx681, 2560x1440 NV12). The daily
stack no longer reads the Windows-derived start-up profile
(`imx681-2560x1440-nv12-v1.bin`). camss module 49 loads
`qcom/sp11/imx681-front-open-v1.bin`, which `install-daily2.sh` generates at install
time from files in this repository. Nothing private is read at build, install or run time.

## What the profile is

A data-only carrier (64-byte header, 2661 register words, 26,036 table bytes) that the
driver places into its own CDM instruction topology (`native-front-profile-schema.h`,
which holds no data). `open-profile/frontprof.py` labels every word: which register in
which packet (start-up P0..P3, steady S, steady module record M), or which DMI table.

## Sources of the open profile

`open-profile/gen-front-open-profile.py` builds it from:

| Part | Source | Status |
|---|---|---|
| Register configuration (559-line list) | `front-ae/tuning/imx681-front-isp-regs.txt` | Mode geometry (3840x2160 to 2560x1440, crop/round/clamp, scalers, DS4/DS16, statistics windows), module enables, pedestal, full-range BT.601 transform (306/601/117 per 1024), identity colour matrix: functional values observed on this machine, the same class as sensor init tables. Our values for BPC_ABF (sweep ae-44..74) and BLS (dark frames). |
| Switched-off modules | Same list | PDPC, GIC, the 0x5460 stage and the GTM tone mapper: enable bit 0 cleared, every other configuration register 0 (the 262 tone-curve registers included); DMI bank selects kept. The ablations of 2026-10-10 showed none of them is needed. |
| Lens shading | `front-ae/tuning/imx681-front-lsc-v1.txt` | Our flat-field measurement (`fit-lsc.py`). |
| Noise LUT | `front-ae/tuning/imx681-front-abf-v1.json` | Our noise model (`gen-abf-lut.py`). |
| Gamma | Generated: sRGB transfer curve | Start-up only; the IPA writes its own curve every frame. |
| PDPC, GIC, 0x5408, GTM, DS4/DS16 filter, BF tables | Zeros | Modules off, DS4/DS16 outputs unused, BF statistics unused on the front. |

The vendor tables (shading, defect, green imbalance, tone mapper curve and registers,
DS4 filter kernel) are not in the open profile. The colour matrix is applied by
`native_front_ccm_q7` (our measurement), as before.

## Proof it programs the same hardware state

`open-profile/compare-front-profiles.py` (lab tool) materializes the private and the
open profile like the driver, applies the daily load-time overrides (CCM, register
masks, LSC, ABF) and lists every capsule difference. Result: differences only in
switched-off modules (PDPC/GIC/0x5460/GTM registers and tables), the start-up gamma
and the unused DS4/DS16 filter tables. Every other register and table word is
identical to what the daily stack (run 93 configuration) programmed.

## Hardware A/B (daily camera boot, same scene, `open-profile/capture-ab.sh`)

Run A: module 48 + private profile. Run B: module 49 + open profile, with the private
file moved out of every firmware path. Both 600/600 frames, ~25.5 fps, no metadata
mismatches, no kernel warnings. Dark room, analogue gain 16.

| Metric (3 frames vs 3 frames) | A vs A (control) | A vs B |
|---|---|---|
| Fixed exposure: mean abs dY | 1.450 | 1.451 |
| Fixed exposure: edge strength ratio | 0.758 | 0.755 |
| Fixed exposure: HF energy ratio | 0.944 | 0.956 |
| Fixed exposure: U/V delta (flat) | 0.57 / -1.99 | 0.77 / -1.93 |
| Automatic: mean abs dY | 2.821 | 2.820 |
| Automatic: HF energy ratio | 0.959 | 0.964 |

The open profile is indistinguishable from the private one within run-to-run noise.
Both webcam bridges (`/dev/video50`, `/dev/video51`) stream normally on module 49.

## Reproduce

    python3 open-profile/gen-front-open-profile.py native-front-profile-schema.h \
      front-ae/tuning/imx681-front-isp-regs.txt front-ae/tuning/imx681-front-lsc-v1.txt \
      front-ae/tuning/imx681-front-abf-v1.json out.bin
    # sha256 e015b799b9a1a46b62f541750f050d639f99b1ebf0eb1598d5441cd9ca9f3981

`unified/build-kernel49.py out.bin` builds module 49 (module 48 with the open file
name and digest). `extract-front-regs.py` documents how the register list was derived.

## Remaining

- Rear camera: the daily rear still reads `rear-generation-20261007-60.bin` (rear
  shading tables and tone-mapper curve from the Windows rear tuning, plus functional
  geometry/statistics values). Same method applies.
- Upstream form: the register list should become driver code / a params-buffer uAPI
  (libcamera), not a firmware file; the start-up register list should be reduced to
  explained registers for review.
