# E004nr — first isolated, compiled Linux rear 4K CSI1/VFE1 profile

## Result: source-compiled rear graph preflight, hardware runtime still denied

Parent: E004nq verified physical-register commit `5fe969444e44f79f6b2efba44be6e60017d2f2b3`. This is the first NEW Linux kernel source implementation staged from those rear-specific OEM Windows live MMIO facts, not a reuse of the older rear VFE0 source-only hypothetical route E004nk/E004nl. This experiment does **not** create a Linux rear-native processed frame or authorize a camera activation.

On SP11 protected Golden `7.1.5-sp11-render-parity-v4+`, kernel boot ID `478d9147-1333-4625-b736-ada9849b0547`, the source-pinned `stage-build.sh` copied the **existing accepted integrated Qualcomm CAMSS** source to a *new, isolated, non-installed* module-build directory. The original `camss.c` SHA256 is `788243cbf08d1f8cc1500a8c7177e30095875bd3b3be54bf0ac0fdec106dba91`; its byte-for-byte content is preserved in the staged build except for one adjacent `#include "camss-e004nr-rear-profile.inc"` inserted **after the existing shared media-link helper and immediately before the unmodified front-specific runner**. Neither the accepted integrated kernel source nor any Golden kernel/DT/initrd/module file was modified. Pre-existing dirty `arch/arm64/boot/dts/qcom/x1-microsoft-denali.dtsi` in the integrated kernel tree was left untouched. Existing front E003i native-VFE1 27-frame runtime path, E004lr Linux rear VFE0 RAW diagnostics and E004ne software rear4K fallback all remain untouched.

The NEW `camss-e004nr-rear-profile.inc` is real compilable kernel source, deliberately unreachable from probe, ioctl, sysfs, stream-on or current E003h front runner. It provides a **source-locked, rear-only** graph preflight returning 0 only after all these tests:

- Actual SP11 X1E CAMSS/OV13858 GRBG input 4076×2806 on **CSIPHY1, four-lane D-PHY**, genuine sensor entity and bound host-private PHY identity;
- configured **CSID1 PIX enabled** for rear, correct RAW10 Bayer `MEDIA_BUS_FMT_SGRBG10_1X10` throughout the CSID/VFE sink path, and full bidirectional live media-pad connectivity rear sensor → CSIPHY1 → CSID1 PIX → VFE1 PIX → its correct V4L2 video entity;
- explicit VFE1 full, non-lite core; requires source pads and CSID sink reverse links to prevent inadvertent front-sensor cross-ownership of shared CSID1/VFE1. A disconnected or front IMX681 CSI PHY is rejected;
- SOURCE-ONLY scalar descriptor from two E004nq Windows 4K rear physical runs: CSID1 RX_CFG0 `0x10232103` (4-lane DPHY PHY_NUM_SEL2), IPP CFG0/CFG1 `0x802b2000/0x00007241`, cropped input x0..4063/y0..2285 → 4064×2286, preserved GRBG Bayer phase, VFE1 FULL output Y3840×2160/C3840×1080 physical stride5120 packer0xb.

The separate **`camss_e004nr_rear_pix_runtime_authorization()` always returns `-EOPNOTSUPP`**, even when graph preflight returns 0; rear hardware/optical frame is NOT verified. Profile flag `linux_rear_4k_hardware_authorized=false`. `__used` retains the function and static profile in the compiled module for inspection but there is **no caller**; no new user-visible trigger, fallback change, module parameter or probe path was introduced. The original front-only `camss_x1e_pix_runner_validate` body remains unchanged and remains CSIPHY2/CPHY/IMX681-specific.

## New rear write-master output register evidence — not a Linux allocation proof

The new `extract-sp7-rear-vfe-output-scalar.ps1` re-reads SP7's existing **private, same-machine E004nq** 5-phase `dd /p` snapshots, whitelists just VFE1 WM0/1/2/3 and enabled statistics WM11/12/13/14/16/18 nonpointer configuration dwords and requires exact equality of every extracted field between LIVE1 and LIVE2. It does **not** retrieve `IMAGE_ADDR` (+0x04), `META_ADDR` (+0x40), frame RAM, Windows IOVAs, optical pixels, images, thumbnails or hashes. Original raw SP7 KD logs remain private SP7. The filtered `WM-RESULT.json` contains only these two matching sets of register-configuration scalars. New measured rear-specific Windows values used in the compiled profile:

| VFE1 write master | Image geometry | Physical WM stride | `FRAME_INCR` | `PACKER_CFG` | `META_CFG` | `MODE_CFG` |
|---|---|---:|---:|---:|---:|---:|
| WM0 FULL_Y | 3840×2160 | 5120 | `0x00a9d000` | `0x0000000b` | `0x00000800` | `0x00000023` |
| WM1 FULL_C | 3840×1080 | 5120 | `0x00559000` | `0x0000000b` | `0x00000800` | `0x00000033` |
| WM2 DS4 | 480×270 | 3840 | `0x0010e000` | `0x0000000a` | `0x00000000` | `0x00000000` |
| WM3 DS16 | 120×68 | 1024 | `0x00018000` | `0x0000000a` | `0x00000000` | `0x00000000` |

For both FULL WM the physical `IMAGE_CFG1=0`, `WM_CFG=0x11`; all listed scalar fields match across TWO independently stopped/restarted real Windows rear captures. `FRAME_INCR` is a **physical output write-master register**, NOT a claim that a Linux V4L2 NV12 buffer can simply be allocated with that length/stride or that required UBWC metadata, output compression, IOMMU or SMMU ownership are understood. Do not claim `0x00a9d000 + 0x00559000` is proven safely sufficient for Linux 4K user-space allocation. Windows' application-visible NV12 3840×2160 remains a separate contract. The actual rear Linux ISP IQ/3A and RT-CDM packet/data generation remain **unimplemented**.

## Real ARM64 build and checks

`stage-build.sh` checked the protected Golden guard, exact integrated CAMSS base source and new profile SHA256 before staging. It built the isolated CAMSS module against `/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826` on SP11 using `make -C "$HEADERS" M="$B" W=1 -j4`. The **current v2** compiled module is stored locally, **not installed or exported**, at:

`/home/geoca/Documents/SP11-PROJECT/02-kernel/e004nr-rear-pix-profile-build-v2/camss/qcom-camss.ko`

It compiled without compiler warnings/errors. SHA256 `5bbb584e6ce01b20cc7fb24b0ee5201409c493be3d9ef5e72420ba91d0e7e9fc` (13,534,176 bytes), `vermagic 7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`. `aarch64-linux-gnu-nm -a` confirmed all three new compiled symbols: `camss_e004nr_rear_oem_profile`, `camss_e004nr_rear_pix_graph_preflight`, and `camss_e004nr_rear_pix_runtime_authorization`. The staged full `camss.c` SHA256 is `03e3138e6ac10725e0a5bdfda4128344d0d3c75e904268fb1fbf0aacb8514c01` and removing the one added include gives **exact original front runner/CAMSS source bytes**.

`BUILD-RESULT.json` preserves only the verified build SHA, module version, retained symbol names and no-load/Golden-safety status for GitHub review; the 13 MB binary itself remains on SP11 and is not exported. `verify.py` also independently checks this build-result manifest.

`verify.py` validates the original E004nq source-backed 2-live/5-phase physical route, the new independent WM whitelist in both passes, every compiled profile constant against the OEM dwords, exact front-source preservation, explicit runtime block, actual retained symbols and module SHA/vermagic, plus **15 fail-closed negative mutation tests** (wrong PHY, front-injected crop/stride/frame-incr, mismatched second pass, WM pointer leakage, wrong metadata/mode, fake rear Linux hardware proof, falsely-active VFE0 and POST-not-IDLE). Run:

```sh
cd /home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
PYTHONDONTWRITEBYTECODE=1 python3 experiments/E004-front-ir-vd55g0/e004nr-rear-pix-kernel-source-profile/verify.py
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process
```

**Next engineering dependency:** keep this rear graph proof independent of front E003i. Implement and validate distinct OV13858 CSID1 IPP source-crop programming, 4K physical WM output surface/UBWC metadata and RT-CDM/IQ/3A producer with proven Linux IOMMU-safe allocation and exclusive frontend ownership; do not promote the current kernel profile into a runtime arm until those are source-locked and a Golden-safe one-shot first-frame test is ready. Windows physical rear 4K output path is proven. Linux native rear hardware 4K ISP output is **not** proven. SP11 Golden was not rebooted or asked to suspend in this experiment.
