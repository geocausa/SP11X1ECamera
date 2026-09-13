# E004bd — Windows secure-CSIPHY dynamic parity

## Result

**PASS: Windows dynamically proves the protected Surface IR route uses secure-lane mask `0x8`, and Qualcomm's public Linux secure-CSIPHY algorithm independently computes the same `0x8` for the Windows-proven SP11 IR topology.**

This checkpoint follows the project rule that Windows is the parity oracle. The Linux/public-source work is used only to map the already-observed Windows behavior into an implementation shape.

No Linux secure-camera call was executed.

## Windows oracle

The accepted E004aq KD trace captured the real protected IR transition.

Enable side:

- SecureISP lane dispatch command `0x2e`;
- lane-protection mask `0x8`;
- `ConfigSecureCamera(..., lane_mask=0x8, protect=1)`.

Teardown side:

- SecureISP lane dispatch command `0x2f`;
- the same lane-protection mask `0x8`;
- `ConfigSecureCamera(..., lane_mask=0x8, protect=0)`.

This is dynamic same-machine authority. It is not reconstructed from Linux.

The underlying E004aq run also proved the Windows Hello/source-controller SecureMode sequence and real protected IR frame delivery.

## Windows-proven physical topology

E004j independently established from the live Windows CSIPHY0 image:

- CSIPHY index 0;
- two-phase / D-PHY;
- one data lane;
- receiver data-lane position 0;
- normal receiver lane-enable mask `0x81` (clock bit plus data lane 0).

## Qualcomm Linux cross-check

Qualcomm's public camera driver computes the secure CP lane mask from the active physical lane assignment.

For the Windows-proven SP11 topology:

1. one active data lane at position 0 gives `lane_assign_bitmask = BIT(0) = 1`;
2. CSIPHY index 0 contributes no per-PHY block offset;
3. D-PHY placement shifts the data-lane mask by `CAM_CSIPHY_MAX_CPHY_LANES = 3`;
4. therefore the secure mask is `1 << 3 = 0x8`.

That is an exact match to the live Windows mask.

The same public driver then calls its secure-camera compatibility hook with:

- the protect/unprotect boolean;
- the computed `csiphy_cpas_cp_reg_mask`.

Its lifecycle is also symmetric: secure protection is requested during secure start and cleared on stop/release.

## Current upstream Linux gap

The project's 7.1.5 kernel has the generic Qualcomm SCM transport but does not expose the camera-specific `qcom_scm_camera_protect_phy_lanes()` wrapper used by Qualcomm's camera driver.

E004as already decoded the installed Windows request as the Qualcomm SIP camera service/command pair and established that it carries exactly two value arguments: protect state and lane mask.

Therefore the gap is now narrow:

**Windows-observed behavior and Qualcomm Linux camera semantics agree; the local 7.1.5 tree is missing the camera-specific SCM wrapper/integration.**

## Why this matters

The secure CSI transition is no longer an opaque Windows-only operation and no longer needs a guessed mask.

For Surface IR, parity authority is now:

`Windows dynamic mask 0x8 == Qualcomm Linux algorithm mask 0x8`.

A Linux implementation should reproduce that exact Windows behavior rather than invent a different lane-protection scheme.

## Evidence

- `evidence/WINDOWS-DYNAMIC-LANE-PROTECTION.txt`
- `evidence/WINDOWS-IR-TOPOLOGY.txt`
- `evidence/QUALCOMM-LINUX-SECURE-CSIPHY.txt`
- `evidence/CURRENT-LINUX-SCM-GAP.txt`
- E004aq accepted protected-Windows dynamic oracle
- E004j same-machine Windows CSIPHY0 topology
- E004as static Qualcomm SIP decode

## Safety boundary

No Linux secure SIP/SCM camera call was executed. No CSI protection state changed under Linux. No camera memory ownership changed. QCOMTEE remains unloaded.

## Next gate

Build a dormant/compile-only 7.1.5 camera-SCM wrapper that represents the Windows-observed protect + lane-mask operation exactly. Do not invoke it at runtime yet. Then wire the wrapper into a parity candidate only after its call shape and rollback lifecycle are mechanically verified.
