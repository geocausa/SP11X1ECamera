# E003h — VFE1 timeout read-only telemetry 0046 one-shot candidate

Distinct candidate for static patch `0046-x1e-vfe1-timeout-readonly-telemetry.patch`. It retains the exact 0045 camera behavior and frozen sensor/DT/capsule/helper/media/observer inputs; only qcom-camss changes to the 0046 module that adds a read-only VFE1 snapshot after the existing Epoch0 timeout.

- GRUB ID: `sp11-camera-e003h-vfe1-0046-one-shot`
- boot directory: `/boot/sp11-7.1.5-camera-e003h-vfe1-0046`
- marker: `sp11_camera_e003h_vfe1_0046=1`
- CAMSS SHA-256: `f1b5ce5dc973a140b29257927c02b2749f96f379fc01b78a10841443a15ab4be`

Static inspection proves 30 `readl_relaxed()` telemetry accesses, zero added MMIO writes, zero added polling primitives, and no start/stop/IRQ-clear/buffer-programming change. The snapshot is called only after the existing VFE1 Epoch0 poll times out.

Binary `.ko/.dtb/.bin` runtime assets are intentionally Git-ignored but frozen in this package and pinned by `asset-manifest.json`. Package scripts and inspection metadata are tracked. The package gate requires Golden current/saved default, empty `next_entry`, bounded provenance green, no camera modules loaded, and no `AUTHORIZATION.json`.

**Package state is unarmed and runtime unauthorized.** A hardware diagnostic requires a later fresh authorization checkpoint after this package is committed and pushed.
