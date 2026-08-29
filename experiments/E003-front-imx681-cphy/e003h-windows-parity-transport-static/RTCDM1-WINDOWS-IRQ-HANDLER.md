# E003h exact Windows RT-CDM1 IRQ-handler oracle

The exact installed `qccamisp8380.sys` remains the behavioral authority. A fail-closed Capstone extractor pins handler RVA `0x29120..0x2930c` in SHA-256 `64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c`.

The handler loads the mapped RT-CDM base from object `+0x48`, reads FIFO status directly at `+0x44/+0x144/+0x244/+0x344`, and masks every status with `0x00070007`. It contains **no read of IRQ_CONTEXT_STATUS +0x2c**. When FIFO0 has a recognized status, Windows writes the masked per-FIFO values to CLEAR `+0x34/+0x134/+0x234/+0x334`, then writes `1` to CLEAR_CMD `+0x38/+0x138/+0x238/+0x338`.

This closes two Linux mismatches that existed in the first PIX attempt: Linux incorrectly required `IRQ_CONTEXT_STATUS bit0` before reading FIFO0 status, and it wrote raw status rather than `status & 0x00070007` to FIFO0 CLEAR. The first mismatch can suppress a legitimate reset-done or BL-done completion if the context register does not carry the assumed bit. That is a plausible explanation for the observed 500-ms-class timeout, but the failed run did not log the exact stage, so causality is not claimed.

Static `0037-x1e-rtcdm-irq-handler-windows-parity.patch` removes the unproven context gate and clears only the Windows-masked known status. Unknown/error raw bits still fail closed after known status acknowledgement. No new runtime is authorized by this correction.
