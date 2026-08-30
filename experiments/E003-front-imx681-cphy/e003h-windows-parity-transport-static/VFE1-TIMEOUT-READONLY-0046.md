# E003h 0046 — VFE1 timeout read-only telemetry

0045 fixed the missing per-startup VFE1 CHANGE_BASE wrapper and restored CSID1 `BUF_DONE_IRQ_MASK` to the Windows value, but the bounded path still times out before VFE1 raw Epoch0. 0046 is therefore diagnostic only: it adds a VFE1 snapshot at the already-existing Epoch0 timeout and changes no camera programming or lifecycle.

The telemetry allowlist is pinned by `vfe1-timeout-readonly-telemetry-oracle.json`. It includes TOP/BUS IRQ status and masks, BUS write violation/overflow/image-violation status, VFE1 live-stable startup readback offsets `+0x90/+0x94/+0x98`, and FULL client0/1 configuration. Dynamic image/meta address registers are compared only against Linux-owned slot-0 IOVAs calculated by the existing bus address builder; Windows dynamic addresses are never copied or compared.

Patch `0046-x1e-vfe1-timeout-readonly-telemetry.patch` adds the snapshot helper and calls it only after `vfe680_x1e_pix_runtime_poll_epoch0()` returns an error. Strict checkpatch reports zero errors/warnings/checks and reverse/forward reconstruction is byte-identical. The fail-closed inspector proves 30 `readl_relaxed()` accesses, zero added MMIO writes, zero added polling primitives, unchanged CSID source, and no start/stop/IRQ-clear/buffer-programming change.

No runtime is authorized by this checkpoint. The next gate is a distinct 0046 one-shot package with the same frozen 0045 sensor/DT/capsule/helper inputs and only the new CAMSS module changed. Any run requires a fresh authorization review after that package is committed and pushed.
