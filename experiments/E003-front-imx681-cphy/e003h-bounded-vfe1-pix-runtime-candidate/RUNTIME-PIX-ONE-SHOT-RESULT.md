# E003h VFE1 PIX one-shot runtime result — 2026-08-29

The single authorized `sp11-camera-e003h-pix-one-shot` attempt was executed once and was not retried.

Pre-RUN checks passed on the disposable candidate: pinned qcom-camss, capsule and helper hashes matched; the front-only media graph was `IMX681 -> CSIPHY2 -> CSID1 PIX -> VFE1 PIX -> /dev/video7`; `/dev/video7` enumerated only QC10C at 2560x1440; IMX681 and CAMSS were runtime-suspended before the trigger.

The helper issued exactly one `RUN`. The sysfs write returned `ETIMEDOUT`; elapsed wall time from helper start to failure was about 0.76 s. No QC10C output file was created. The kernel log contains no `MODE_SELECT=1` / front-transmission-start message, so failure occurred before sensor transmission. The current trigger did not emit per-RT-CDM stage diagnostics, therefore this run alone cannot distinguish a reset-done timeout from the first FIFO0 BL-done timeout and must not be over-interpreted.

Post-failure checks on the same candidate boot showed IMX681 and CAMSS runtime-suspended and no kernel fault/panic. The irreversible one-shot latch was respected: no same-boot retry occurred. The machine was immediately rebooted.

Golden return is verified: kernel `7.1.5-sp11-render-parity-v4+`, `BOOT_IMAGE=/boot/sp11-7.1.5-audio-fullio-v19c/...`, `saved_entry=sp11-audio-fullio-v19c`, empty `next_entry`, byte-exact Golden kernel/initrd, and no candidate camera module loaded.

Evidence hashes:
- `RUNTIME-PIX-MEDIA-PREFLIGHT.txt`: `afa0092fa4d3ecd3e4759ef186d7bc672404d86aa4e675150846eef5ae7b972e`
- `RUNTIME-PIX-ONE-SHOT-20260829.txt`: `5afe12491657d945c15f985a1c6ece59a2cfd327009d6c86f70d202763b89364`
- `RUNTIME-PIX-ONE-SHOT-PRE-REBOOT.txt`: `d612ffb2e44ea7a706bd4a8ff22877f55e0be23df69b4e7299aeb87711d23ac7`
- `RUNTIME-PIX-PREVIOUS-BOOT-KERNEL.txt`: `4d8ca04078fec7e4bb6decbac381aa5dac4be29c0e28dfe71fd2d87016577467`

Accepted consequence: do not repeat the PIX attempt. First add static, fail-closed RT-CDM stage diagnostics that distinguish preflight/open-reset, core-start, and individual FIFO0 BL completion boundaries; build and inspect them on Golden. A future diagnostic runtime requires a new explicit one-shot authorization checkpoint.
