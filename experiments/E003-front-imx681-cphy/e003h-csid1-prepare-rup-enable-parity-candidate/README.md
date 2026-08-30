# E003h — CSID1 prepare → RUP/AUP → enable 0043 one-shot candidate

Fresh runtime package for static patch `0043-x1e-csid1-ipp-prepare-rup-enable-order.patch`.

It reuses the proven Golden kernel/initrd, accepted front-only DTB, IMX681 module, PIX capsule/helper, media setup and persistent RT-CDM observer. The only camera-code change is the 0043 `qcom-camss.ko` that stages CSID1 IPP before the already-existing prime1 RUP/AUP and performs only the proven IPP enable afterwards.

- GRUB ID: `sp11-camera-e003h-csid1-0043-one-shot`
- boot directory: `/boot/sp11-7.1.5-camera-e003h-csid1-0043`
- command-line marker: `sp11_camera_e003h_csid1_0043=1`
- candidate CAMSS SHA-256: `23cc63f742f70ca3f70e25d89b34c9e8cef531ed6f3c9562f2f7b0d3a7ac05a9`

Package creation/installation does not authorize or arm runtime. `AUTHORIZATION.json` must be absent until a separate post-package checkpoint explicitly authorizes one boot and one helper invocation.
