# E003h — CSID1 IPP start parity one-shot candidate

This package is the fresh runtime gate after static patch `0042-x1e-csid1-ipp-start-windows-parity.patch` closed the Windows CSID1 IPP start boundary.

It reuses the already-proven Golden kernel/initrd, front-only DTB, IMX681 module, PIX capsule, helper, media setup and persistent RT-CDM observer from the prior consumed package. The only camera-code change is the newly built qcom-camss module SHA-256 `c67ce602f88be5db2ffecd816879081d74f996f7884e8661bea252d924f7098e`.

Fresh boot identity:

- GRUB ID: `sp11-camera-e003h-csid1-0042-one-shot`
- boot directory: `/boot/sp11-7.1.5-camera-e003h-csid1-0042`
- command-line marker: `sp11_camera_e003h_csid1_0042=1`

The installer never arms `next_entry`. The package inspector must pass while Golden remains the saved default and camera modules are unloaded. `AUTHORIZATION.json` is intentionally absent from the package checkpoint and is required by `run-once.sh`; runtime is therefore unarmed until a separate authorization commit.
