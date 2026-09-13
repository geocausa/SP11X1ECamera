# E004bb — Windows Surface IR Lite-selector dynamic oracle

## Result

**PASS: the exact protected Surface IR DeviceConfig sent to CameraSecureISP carries feature flag `0x2`, explicitly setting Qualcomm's `CAM_ISP_CAN_USE_LITE_MODE` bit.**

The value was observed twice independently during one bounded Windows run using the already-accepted Windows Hello/source-controller trigger.

Linux SecureISP runtime was not used.

## Why this experiment existed

E004ba statically established that DeviceConfig dword `0x23` is the Qualcomm camera `feature_flag` field and that its bit 1 is `CAM_ISP_CAN_USE_LITE_MODE`. The only missing fact was the live Surface IR value.

E004bb measured that value at the CameraSecureISP DeviceConfig handoff without modifying the payload.

## Dynamic result

Both observed DeviceConfig transactions had:

- DeviceConfig command `0x802`;
- payload length `0x900`;
- feature-flag dword index `0x23` / byte offset `0x8c`;
- feature flag **`0x00000002`**.

Therefore bit 1 is set in the exact live protected Surface IR configuration.

This closes the selector chain:

**Windows Surface IR protected route -> feature_flag bit 1 -> CAM_ISP_CAN_USE_LITE_MODE -> SecureISP Lite-capable CSID selection.**

Combined with E004ax, the same protected configuration uses logical IFE core 3, which E004aw maps to IFE-Lite. E004ay/E004az then show that Linux already implements the corresponding X1E VFE680/CSID680 register families.

## Trusted trigger / frame validity

The run reused the accepted E004aq Windows Hello source-controller sequence:

- Surface IR FaceAuth profile;
- NV12 644x604 at 60 fps;
- FaceAuthMode enable succeeded;
- SecureMode enable succeeded;
- 12 real IR frames were acquired;
- SecureMode remained enabled during streaming;
- teardown returned both controls to disabled.

The experiment therefore observes the selector during the same class of protected route that is known to deliver real frames.

## Debugger scope

The debugger observation was read-only. It observed the DeviceConfig payload presented to CameraSecureISP and did not alter the request or camera state.

The full raw KD log remains retained on SP7 and is pinned by byte count and SHA-256 in the evidence summary.

## Golden return

The one-shot Windows boot returned to unchanged Golden Linux:

- kernel `7.1.5-sp11-render-parity-v4+`;
- `sp11_entry=7.1.5-sp11-fullio-v19c`;
- saved GRUB entry `sp11-audio-fullio-v19c`;
- empty `next_entry`;
- BootCurrent `0005`;
- boot order unchanged;
- no media/video nodes;
- no camera or QCOMTEE modules loaded.

## Evidence

- `PREBOOT-LINUX.txt`
- `POSTRETURN-GOLDEN.txt`
- `evidence/E004BB-KD-DEVICECONFIG.txt`
- `evidence/E004BB-WINDOWS-RUN-SUMMARY.txt`
- E004ba semantic authority for the public Qualcomm feature bit
- E004aq accepted trusted-trigger authority

## Architectural consequence

The Windows protected route is no longer merely inferred to be Lite from register behavior. The host explicitly marks the secure input resource as Lite-capable.

That substantially narrows Linux parity work: Linux already knows the ordinary X1E Lite register model; the remaining hard problem is reproducing the **protected ownership, trusted-execution transport, memory-domain transition and lifecycle**, not choosing or inventing a different camera datapath.

## Safety boundary

All protected runtime activity in E004bb occurred under the installed Windows stack. Linux remained outside the SecureISP/QCOMTEE runtime path.

## Next gate

Inventory the SP11 firmware/trusted-application environment and Linux QCOMTEE object model statically. Determine whether a camera/ISP trusted application already exists in firmware and what loader/session mechanism would be required. Do not execute a Linux secure-camera session yet.
