# E004aj — Windows SecureMode trigger dynamic gate

Goal: exercise the exact Windows SecureMode path identified by E004ai instead of repeating the plain WinRT holder from E004ah.

Trigger:
- exact source group: Surface IR Camera Front
- KSPROPERTYSETID_ExtendedCameraControl = 1CB79112-C0D2-4213-9CA6-CD4FDB927972
- property ID = 36 (KSPROPERTY_CAMERACONTROL_EXTENDED_SECURE_MODE)
- filter scope
- enabled flag = 2; disabled flag = 1
- payload = 40-byte KSCAMERA_EXTENDEDPROP_HEADER + VALUE

Acceptance requires:
1. SecureMode GET/SET/GET through VideoDeviceController succeeds.
2. KD proves surfacecamavs setter +0x83120 receives value 2 and state +0x2ad becomes 1.
3. Real IR frames are acquired while SecureMode is enabled.
4. Preferably hit secure KMDISP call +0x9da0 with operation 2 and 12-byte CSI payload.
5. Any qccamsecureisp task/lane evidence must come from current relocated image only.
6. Clean disable/stop and one-shot return to protected Golden.

Linux SecureISP runtime remains forbidden.
