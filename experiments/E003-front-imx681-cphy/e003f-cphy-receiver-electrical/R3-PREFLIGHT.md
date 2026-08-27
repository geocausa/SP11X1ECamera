# E003f-R3 preflight — host-powered receiver electrical retry

R2 crossed the corrected 8 KiB MMIO aperture and completed CSIPHY2 local power-on, but the live Windows-register comparison found 78 mismatches: all expected non-zero lane/common values remained zero. CTRL5/6/7 were also zero. The R2 harness unwound cleanly; CSIPHY2/timer clocks and receiver rails returned to zero, and IMX681 remained reset/off.

Static trace of normal CAMSS power ordering shows that host pipeline power brings up a VFE parent before downstream receiver activity. On X1E VFE0 `vfe_get()` enables the IFE0 domain plus CAMNOC, CPAS AHB/fast-AHB and VFE clocks. R2 called CSIPHY2 `.s_power` directly and therefore omitted that host-side context.

R3 keeps the corrected 8 KiB DTB and patched CAMSS unchanged. The test harness now executes only:

1. validate CSIPHY2 MMIO resource >= 0x2000 and C-PHY one-trio config;
2. VFE0 `.s_power(1)` to establish host IFE/CAMNOC/CPAS context;
3. CSIPHY2 `.s_power(1)`;
4. CSIPHY2 `.s_stream(1)`;
5. compare 121 final Windows-live registers;
6. CSIPHY2 `.s_stream(0)` and require CTRL5/6 zero;
7. CSIPHY2 `.s_power(0)`;
8. VFE0 `.s_power(0)` last.

No CSID stream call is made. No IMX681 callback, I2C/CCI transaction, MODE_SELECT write or sensor-power operation exists in the harness.

R3 harness SHA-256: `20c60fa0d6fd5650a1cca51adb78b6697b8b0dbdb70edb692d7c1b2ba105a1f6`.
Golden ABI: 13 imports / 0 CRC mismatches.
Reproducible R3 initrd SHA-256: `082f9aebc0ba19ed2279856c6e7a55b8f9a29c6733586b7430a51c91578fa587`.
Corrected R2/R3 DTB SHA-256: `e9fd13a29b6580955d2662c27377dbd1caba14f7f89613510b5e23bd6c266293`.
Patched CAMSS SHA-256: `e1c8dcb099ee872ffd8bac263576b8f2db85cef104077df80d29a2916f47f308`.
