# E004ba — SecureISP Lite-selector semantic map

## Result

**PASS: the trustlet DeviceConfig selector at manager +0xe00 is the public Qualcomm `CAM_ISP_CAN_USE_LITE_MODE` feature bit.**

This is a semantic/static result. The exact live SP11 Surface IR feature-flag value is intentionally left for a bounded Windows observation.

No Linux SecureISP runtime occurred.

## Exact structure match

The trustlet DeviceConfig handler logs and consumes a dword array whose field ordering matches Qualcomm's public `cam_isp_in_port_info_v2` structure:

- dword 0: resource type
- dword 1: lane type
- dword 2: lane count
- dword 3: lane configuration
- dwords 4..7: VC array
- dwords 8..11: DT array
- dword 0x0c: valid VC/DT count
- dword 0x0d: input format
- ...
- dword 0x22: `sfe_in_path_type`
- dword **0x23: `feature_flag`**

The public header defines `CAM_ISP_VC_DT_CFG = 4`, making the field positions line up exactly with the trustlet's own diagnostics.

## Selector meaning

The public Qualcomm camera UAPI defines:

- bit 0: fetch security mode
- **bit 1: `CAM_ISP_CAN_USE_LITE_MODE`**
- later bits: dynamic-switch/SFE/AEB/etc. features.

The public camera HW manager decodes `feature_flag & CAM_ISP_CAN_USE_LITE_MODE` into `can_use_lite`, and that value gates whether lite CSID resources may be selected.

The SecureISP trustlet performs the corresponding extraction:

`manager_selector = (feature_flag >> 1) & 1`

and later uses that selector to choose between its two secure CSID HAL tables.

Therefore manager `+0xe00` is not an opaque bit anymore: it is the **Lite-resource eligibility bit derived from the same public Qualcomm feature flag**.

## Distinction from bSfeUsed

This selector is not the same state as the trustlet's separately logged `bSfeUsed` byte.

Keeping them separate matters:

- `CAM_ISP_CAN_USE_LITE_MODE` controls eligibility/selection of the lite CSID family.
- `bSfeUsed` is a separate later pipeline state used for SFE participation.

E004ba does not collapse those states.

## Same-machine Surface corroboration

The installed SP11 `surfacecamavs8380.sys` contains explicit use-case and notification identities for:

- `IFE_LITE_MODE`
- `IFE_LITE_SECURE_MODE`
- secure IFE-Lite frame completion.

That corroborates that the Surface stack has a first-class protected IFE-Lite path, but it is not used as proof of the live feature-flag value.

## Public-source authority

The Qualcomm camera source used for the semantic cross-check was cloned locally from the public Qualcomm Linux camera-driver repository and pinned in the evidence file by commit hash.

## Evidence

- `evidence/QUALCOMM-FEATURE-FLAG.txt`
- `evidence/TRUSTLET-LITE-SELECTOR.txt`
- `evidence/SURFACECAMAVS-LITE-STRINGS.txt`
- `ghidra/SURFACECAMAVS-LITE-CONFIG.txt`
- `ghidra/ExtractSurfaceAvsLiteConfig.java`

## Safety boundary

No QCOMTEE module was loaded. No protected aperture was mapped from Linux. No secure-memory ownership changed. No secure CSI/SecureISP command was issued from Linux.

SP11 remains on protected Golden Linux.

## Next gate

Use the already-proven Windows Hello source-controller trigger in one bounded Windows boot and observe the DeviceConfig feature-flag value passed into CameraSecureISP. This will determine whether bit 1 is set in the exact live Surface IR protected configuration.
