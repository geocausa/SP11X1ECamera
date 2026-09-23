# E004nl — independent rear OV13858 PIX identity and output evidence boundary

Source-only offline C/ARM64 implementation. No camera, kernel, Windows volume, sensor, firmware, DSP or reboot operation is involved. The header is **not** included in the CAMSS kernel and is not an arm/deploy gate. Golden remains protected.

## New distinct findings

1. The accepted IG media graph contains an existing, disabled `msm_csid0` pad4 -> `msm_vfe0_pix` -> `msm_vfe0_video3` link. The rear native RAW proof is instead `msm_csiphy1 -> msm_csid0 -> msm_vfe0_rdi0`. Active rear PIX capture is unproven; video3 is not a stable device pathname.
2. A separate front-only predicate is also embedded in `camss.c`: `camss_x1e_pix_runner_validate()` checks CSID1, CSIPHY2, VFE1, one-lane C-PHY, SRGGB10 3840x2160, and the exact front media links. Its front-specific pending-buffer, RT-CDM and ownership code likewise selects VFE1. `camss-csid-680.c` and `camss-vfe-680.c` have their own front-only predicates. Removing a single condition or enabling an existing rear graph edge does not give a valid rear implementation.
3. Verified front input geometry **3840x2160 SRGGB10** differs from its `camss-vfe-680.c` QC10C **OUTPUT 2560x1440**, stride 3584 and surface size `0x76b000`. These are front-specific output facts, not a 3840x2160 rear hardware contract. The accepted rear RAW *sensor input* is 4076x2806 SGRBG10. Exact Windows rear video sensor-window/ISP crop, output order, Y/C planes/stride/size, 3A and write-master DMA ownership are **NOT established** by a nominal 4K app output.
4. Even the purely geometric center-crop candidate from a 4076x2806 RAW window to 3840x2160 would have horizontal offset 118 and vertical offset 323. The **odd vertical offset changes Bayer row phase**; this is arithmetic only, *not proof that Windows or our Linux ISP uses center-crop*. A blindly reused front Bayer/LSC or guessed crop could give incorrect color. The real rear crop and CFA alignment must be identified from separate source/physical evidence. The independent source-only C helper `sp11_rear_pix_bayer_after_crop()` implements all four crop-offset parity cases for a GRBG mosaic, with an explicit test for the *hypothetical* center-crop. It does not set any Linux kernel/sensor/ISP crop.
5. The installed SP11 Windows rear is OV13858 MSHW0491 (sensor probe ID `0xd855`, see `oracle/windows-rear-kd-2026-08-27.md`) and **not** the MSHW0561 OEM tune. No Windows driver, firmware or tuning payload was copied to the repo.

## Offline route predicate

`rear-pix-route-contract.h` provides a standalone, fail-closed *source identity/route* validator enforcing rear OV13858 MSHW0491 and ID 0xd855, CSIPHY1/CSID0/VFE0, four-lane D-PHY, SGRBG10, 4076x2806, complete graph link flags, IR-off and Linux OS awake. A successful return has the explicit name `SP11_REAR_ROUTE_SOURCE_ONLY`; it **does not** approve MMIO, native ISP frame generation, firmware loading or a candidate boot. Native 4K output proof remains **unconditionally false** in this separate read-only snapshot until actual rear hardware evidence exists.

```sh
cd experiments/E004-front-ir-vd55g0/e004nl-rear-pix-route-contract
cc -std=c11 -Wall -Wextra -Werror -pedantic -O2 test-rear-pix-route.c -o /tmp/e004nl-source-only-test
/tmp/e004nl-source-only-test
```

Use `./run-offline.sh` for the full reproducible ARM64 normal and ASan/UBSan C test plus read-only scanner of the actual checked-out kernel source. It compiles into a unique temporary directory and cleans up its binaries on exit. The scanner pins the three front-only predicates and real rear RAW input while explicitly reporting that the rear native 4K ISP remains unproven. No camera stack installation or module load occurs.

## Next gate — still BLOCKED for physical rear-ISP activation

Derive a **new rear-specific** CSID0 IPP startup/reset/epoch and VFE0 FULL buffer/IOMMU/output spec from actual *rear MSHW0491* Windows driver observations plus accepted Linux sources. Preserve the front predicate and front output policy. Prove rear 4K format/geometry/crop, host IQ/RT-CDM producer, buffer lifecycle and protected Golden fallback independently before preparing a new, unique, source-pinned physical candidate. Do not install/replay stale E003i candidates; no Linux OS suspend or IR illumination.
