# E003h 0073 — TINTCTX camera-identity correction

Status: **accepted offline forensic correction**. No Linux camera runtime and no Linux request6 were performed.

## Correction

The Windows capture session `E003H_20260902_TINTCTX` is **not** the verified IMX681 front stream. It is an **OV13858 rear mode-1** Tintless session.

This does **not** invalidate the byte-exact request5→request6 Tintless replay. It changes what that replay proves:

- it remains an exact proof of the Surface DeviceMFT Tintless implementation and its state carry;
- it is now a strong rear-camera/OV13858 parity oracle;
- it must **not** be spliced into the front IMX681 LSCTRIGSRC/adaptive-live chain or cited as proof that front request5→request6 Tintless state is already closed.

## Mechanical identity proof

A raw NTFS carve recovered the original request5 Tintless `x1` config object, 0x400 bytes, SHA-256:

`b8bb8f82548baa20ea3ce5156d9da1837f65415a6cfc907813c858c7cfcaaffd`

At `TintlessAlgorithmWrapper::Process` RVA `0xc95fd0`, exact DeviceMFT machine code copies the config geometry tuple into the wrapper's internal geometry structure. The captured values are:

| config offset | semantic role | value |
|---:|---|---:|
| `+0x1c` | image width | **4064** |
| `+0x20` | image height | **2286** |
| `+0x24` | horizontal grid cells | **126** |
| `+0x28` | vertical grid cells | **94** |
| `+0x2c` | cell width | **32** |
| `+0x30` | cell height | **24** |
| `+0x34` | grid packing mode | **0** |

The wrapper immediately validates those fields. The exact residual checks are satisfied:

- horizontal: `4064 - 126×32 = 32`, bounded by `2×32 = 64`;
- vertical: `2286 - 94×24 = 30`, bounded by `2×24 = 48`;
- packing mode 0 requires the exact `32×24` cell dimensions.

The same installed Windows Surface sensor authority is decoded by `tools/qti_sensor_summary.py`:

- `com.surface.sensormodule.rfc_ov13858.bin`, SHA-256 `f8f60e79b77bd3d5896cb04167ee428455e1a241f1ff9e50abee6b4dacfe6b14`;
- OV13858 mode **1** is exactly **4064×2286 @30**, crop start **(6,260)**.

The installed front authority:

- `com.surface.sensormodule.ffc_imx681.bin`, SHA-256 `f7dd81be64153fd3f0da8e6288ee1b9906b7bf51b773a98496934d76dc96a45c`;

contains six modes and **none** is 4064×2286. The verified front Windows live capture independently remains full `4048×3152`, crop `(104,496)`, output `3840×2160`, scale 1.

An exhaustive decode of every installed `com.surface.sensormodule*.bin` in the SP11 driver archive finds exactly one 4064×2286 mode: **OV13858 mode 1**. The identity is therefore unique within the installed Surface camera set.

## x23 / geometry boundary remains closed

This correction also rechecked the LSC handoff. `IQInterface::LSC411CalculateSetting` calls:

1. `LSC411Interpolation::RunInterpolation` through table `0x1816204e0 -> 0x18093c1b0`;
2. `LSC411Setting::CalculateHWSetting` through table `0x1816204e8 -> 0x1809b4ba0`.

The calibrated interpolation destination at `param1+0x1e8` is passed directly as `pData` to `CalculateHWSetting`. There is no hidden copy, channel reorder or materialization transform between calibrated `x23` and the geometry resampler. The earlier attempt to force LSCTRIGSRC front `x23` into TINTCTX therefore failed because the sessions are different cameras, not because the geometry implementation was wrong.

## Recovered raw evidence

System Restore removed the later oracle directory metadata, but the NTFS data clusters survived. Exact raw carving recovered:

- front LSCTRIGSRC req5/req6 x22 and x23 buffers;
- TINTCTX req5 input mesh, output-pre mesh, output-post mesh and x1 config;
- TINTCTX req6 post-state.

The proof records their exact partition offsets and hashes in `lsc-tintctx-camera-identity-oracle.json`. These small authoritative bytes are now preserved under `oracle-carved-20260902/`.

## Gate impact

The front integrated LSC gate is now deliberately split:

**Verified front evidence already closed:** rear/default LSC41 x22 source for the front stream, calibrated x23 capture, front geometry/ABI, Tintless-enabled/ALSC-disabled branch, Titan680 staging-to-wire, GIC alias, GTM/TMC, and tuning-manager ownership.

**Still missing for front 1:1 proof:** a genuine **same-front-stream sequential Tintless input/stats/state/output capsule** that can bridge the verified front x23/geometry path into the captured front staging objects.

The old TINTCTX sequential replay is retained under the rear stack and must not be used to satisfy that front gate.

Proof artifacts:

- `prove-lsc-tintctx-camera-identity.py`
- `lsc-tintctx-camera-identity-oracle.json`
- carved bytes under `oracle-carved-20260902/`

Linux request6 remains fail-closed and unauthorized.
