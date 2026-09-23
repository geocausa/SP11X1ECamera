# E004ns — independently compiled rear CSID1 RAW10 IPP register path (OFFLINE)

Parent: E004nr Git `ca5107448610a006b9f618836da42379982234dc`. The previous E004nq same-SP11 Windows rear VideoRecord 4K five-phase hardware oracle measured the true rear CSIPHY1 four-lane D-PHY → **CSID1 IPP → VFE1 PIX** route in TWO separated live sessions. The prior E004nr experiment implemented and compiled a fail-closed Linux rear graph and 4K output-profile check, but explicitly left CSID1's front-only IPP initialization untouched. E004ns is a NEW experiment implementing **a distinct rear CSID1 IPP register configuration function** in a fresh, isolated Qualcomm CAMSS ARM64 build, not modifying the accepted integrated front code or protected Golden.

## New first-party physical-register evidence

`extract-sp7-csid1-rear-config.ps1` was executed **on SP7** against the original **private** E004nq KD `dd /p` physical snapshots of SAME-SP11 Windows rear LIVE1 and LIVE2. It whitelisted exactly 26 CSID1 register *configuration* offsets from the documented CSID680 map (plus CSID0/CSID1 wrapper route and CSID0 IPP control). It never reads optical frames, RAM, DMA addresses, pointers, Windows binaries or proprietary tuning. Both independent rear live sessions matched **ALL 26 final configuration values**. Original SP7 raw KD windows remain on SP7; only filtered, no-pointer `CSID1-RESULT.json` is imported into Git.

| Target register, CSID1-relative | Same value in both live phases |
|---|---|
| RX_CFG0 / RX_CFG1, 0x200 / 0x204 | `0x10232103` / `0x00000001` |
| IPP_CFG0 / IPP_CFG1, 0x300 / 0x310 | `0x802b2000` (RAW10, enabled) / `0x00007241` |
| IPP_CTRL, 0x304 | `0x00000001` |
| IPP parity_zero0 / parity_zero1, 0x324 / 0x330 | `0x00000000` / **`0x02000000`** |
| IPP_EPOCH_IRQ_CFG / both epoch patterns | `0x00130013` / `0xffffffff` each |
| IPP HCROP / VCROP, 0x35c / 0x360 | `0x0fdf0000` (x0..4063) / `0x08ed0000` (y0..2285) |
| IPP format measurement CFG0 / CFG1, 0x384 / 0x388 | `0x0000001f` / `0x08ee0fe0` (configured expected 4064×2286) |
| IPP PIX, LINE and FRAME drop pattern/period | `0x00000000` / `0x00000001` each |
| IPP IRQ subsample pattern / period | `0x00000001` / `0x00000000` |
| top / buffer-done / CSI2 RX / IPP final IRQ masks | `0x00000001` / `0x0001ffff` / `0x019fb800` / `0x3cbc601c` |
| Wrapper IO_PATH_CFG0 | CSID0 `0x00000001` inactive PIX, CSID1 `0x00000101` IFEnabled |

**Important naming correction:** CSID1 offset `0x388` is `CSID_IPP_FORMAT_MEASURE_CFG1` — a programmed dimension expectation, not an independent completed-frame counter. E004nq's earlier scalar decoder called its 4064×2286 value a “measure”; E004ns follows the actual register definition and does NOT claim that field proves a received frame.

**Important front/rear difference:** the existing Linux `__csid_configure_rx()` inserts `TPG_NUM_SEL=1` only for **front C-PHY**. The Windows rear `RX_CFG0=0x10232103` shows `TPG_NUM_SEL=1` as well for **four-lane D-PHY**, without enabling any test-pattern mux. Using that generic helper unchanged would yield `0x00232103` and FAIL Windows rear parity. E004ns computes the complete rear-specific RX word from verified physical lane mapping `0x3210`, 4 D-PHY lanes, OEM PHY_NUM_SEL=2 and its observed selector bit, then rejects any mismatch. It does not change the generic/front receiver helper. Similarly, Windows rear `IPP+0x330=0x02000000` differs from the earlier front companion write of zero.

## Kernel code and safety boundary

The new `camss-csid-e004ns-rear-ipp.inc` has *real compilable* source-only routines `csid_e004ns_rear_ipp_mode0()`, `csid_e004ns_rear_rx_cfg0()`, `csid_e004ns_rear_ipp_prepare()`, `csid_e004ns_rear_ipp_enable()` and `csid_e004ns_rear_ipp_runtime_authorization()`. The first checks X1E CSID1, 4-lane rear CSIPHY1 D-PHY lane map, IPP enabled and GRBG10 4076×2806 input. The separate prepare function validates that Linux's own format decoder produces `0x802b2000` and then provides code to program Windows' *observed final-state* 26-register CSID1 settings. The separate enable function provides CSID1 wrapper output-to-IFE enable and final IPP/IRQ masks. The standalone authorization **always returns `-EOPNOTSUPP`** and the new prepare/enable functions have **no caller whatsoever** in any probe, sysfs, module parameter, V4L2 stream callback, front runner or real currently loaded module.

This source is intentionally **not connected to a hardware stream**: two Windows live *final register snapshots* cannot prove the transient rear initialization order, the IFE1 DSP IQ/RT-CDM programming, safe FULL 4K hardware DMA surfaces including UBWC metadata, IOMMU/SMMU ownership, CSI1/VFE1 sharing/exclusion lifecycle, sensor-specific 3A, or safe read-back teardown. The rear CSID1 source is not a substitute for those. It must not be copied into the Golden kernel or armed based solely on a successful compile.

## Isolated ARM64 build, tests and provenance

`stage-build.sh` source-pins exact original integrated `camss.c` and `camss-csid-680.c`, and source-pins the E004nr rear graph and new E004ns CSID header. It copies the source into a **new isolated build directory** and inserts the previous E004nr profile header into `camss.c` and the E004ns rear CSID header into `camss-csid-680.c` immediately before `__csid_configure_top`. It leaves EVERY original source byte unchanged if those two extra includes are removed, including front `__csid_sp11_front_ipp_mode0`, original front runtime and diagnostics and existing Linux rear CSID0/VFE0 RAW path. The integrated kernel tree's pre-existing modified Denali DTS was never altered. It compiles against prepared Golden-version ARM64 headers with `W=1 -j4` without any compiler warnings/errors.

The isolated, **uninstalled/unloaded** compiled artifact resides only on SP11 at `/home/geoca/Documents/SP11-PROJECT/02-kernel/e004ns-rear-csid-ipp-build/camss/qcom-camss.ko`, SHA256 `8f500bc15226cec583272c5b202b38ff1f9fb2d7a56a7d9b7de6370711ccfc90`, size 13,612,240 bytes, matching Golden kernel vermagic `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`. `aarch64-linux-gnu-nm -a` confirmed the retained rear CSID1 mode/RX/prepare/enable/deny symbols **and** previous E004nr rear graph/deny symbols. The only build artifact committed to Git is the safe scalar metadata `BUILD-RESULT.json`, not the module or OEM Windows binaries.

`verify.py` requires identity and consistency of BOTH E004nq physical phases, BOTH E004ns whitelisted CSID1 snapshots, all 26 C source constants and field layout/semantics, new rear D-PHY TPG bit, rear-only parity-zero1, exact unmodified original front CAMSS/CSID source bytes, actual ARM64 module hash/vermagic/symbol retention and **17 fail-closed negative cases** (front vs rear lane/PHY, crop, TPG, +0x330, wrong DT/IRQ/epoch, live-pass mismatch, CSID0/VFE0 substitution, fake Linux optical-frame proof). Run offline on Golden:

```bash
cd /home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
PYTHONDONTWRITEBYTECODE=1 python3 experiments/E004-front-ir-vd55g0/e004ns-rear-csid1-ipp-offline/verify.py
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process
```

Next: implement and validate the rear-specific VFE1 FULL 4K output/metadata/IOMMU and independent IQ/3A RT-CDM lifecycle using the proven E004nq/E004nr register contracts; only then attach a guarded runtime caller for the isolated rear CSID1 path. Keep front E003i hardware27, rear E004lr RAW, rear E004ne complete software4K fallback and protected Golden intact. **No Linux-native rear optical 4K ISP frame is proven by this E004ns source-only compile.**
