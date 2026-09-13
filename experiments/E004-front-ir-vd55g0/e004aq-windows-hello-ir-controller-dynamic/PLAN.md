# E004aq — Windows Hello IR source-controller dynamic oracle

Goal: reproduce the Windows Hello control sequence recovered in E004ap without invoking Linux SecureISP.

Acceptance:
1. Boot Windows one-shot only; Golden GRUB saved_entry remains untouched.
2. Initialize Surface IR FaceAuth profile.
3. Use IR MediaFrameSource.Controller, not VideoDeviceController.
4. GET exact property strings `{1CB79112-C0D2-4213-9CA6-CD4FDB927972},35` and `,36`.
5. Preserve returned >=40-byte buffers and modify only Flags at +0x10.
6. FaceAuthMode enable succeeds (Flags 2 preferred; 4 only if capability requires it).
7. SecureMode capability bit 1 is present and enable succeeds with Flags 2.
8. KD proves surfacecamavs SecureMode setter receives the transition and, ideally, secure CSI / qccamsecureisp control targets execute.
9. Acquire real IR frames while secure mode is enabled.
10. In finally: stop reader, SecureMode Flags 1, FaceAuthMode Flags 1.
11. Reboot directly back to protected Linux Golden and verify no camera nodes/modules.
12. Linux SecureISP runtime remains unauthorized until this Windows gate passes.
