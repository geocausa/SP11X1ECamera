# E004bb — exact Windows SecureISP Lite-selector dynamic oracle

Goal: observe the exact CameraSecureISP DeviceConfig feature_flag used by the already-proven Windows Hello / Surface IR protected route.

Method:
1. Preserve Linux Golden preboot authority.
2. One-shot boot SP11 directly to Windows.
3. Attach SP7 KDNET before the protected IR trigger.
4. Identify the live CameraSecureISP driver base.
5. Observe the DeviceConfig dispatcher when the trusted Windows Hello source-controller sequence executes.
6. Record the DeviceConfig payload size and feature_flag dword; test bit 1 only as the E004ba CAM_ISP_CAN_USE_LITE_MODE semantic.
7. Avoid modification of payload/state.
8. Run the proven E004aq source-controller trigger and require clean control teardown.
9. Return immediately to Golden Linux and verify unchanged boot/kernel/camera state.

No Linux SecureISP/QCOMTEE runtime is part of E004bb.
