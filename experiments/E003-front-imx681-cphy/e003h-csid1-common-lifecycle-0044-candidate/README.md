# E003h — CSID1 common lifecycle 0044 one-shot candidate

Fresh package for static patch `0044-x1e-csid1-common-lifecycle-windows-parity.patch`.

It reuses the byte-proven Golden kernel/initrd, accepted front-only DTB, IMX681 module, PIX capsule/helper, media setup and persistent RT-CDM observer. The only camera-code change from the consumed 0043 package is qcom-camss SHA-256 `98b3252e9d1e8c46e81ea48fe0a6b4b0ecea77e1206915b4b1378040dc473cbc`, which implements the exact front-mode0 Windows CSID1 common reset/config/companion/enable/stop lifecycle closed by static 0044.

- GRUB ID: `sp11-camera-e003h-csid1-0044-one-shot`
- boot directory: `/boot/sp11-7.1.5-camera-e003h-csid1-0044`
- command-line marker: `sp11_camera_e003h_csid1_0044=1`
- candidate CAMSS SHA-256: `98b3252e9d1e8c46e81ea48fe0a6b4b0ecea77e1206915b4b1378040dc473cbc`

Package creation/installation **does not authorize or arm runtime**. `AUTHORIZATION.json` must be absent at this gate. The installer must leave Golden as `saved_entry` and `next_entry` empty. A hardware RUN requires a later, separate authorization checkpoint.
