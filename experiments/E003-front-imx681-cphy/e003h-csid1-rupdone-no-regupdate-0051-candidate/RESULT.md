# E003h 0051 — front RUP_DONE ownership differential result

The single authorized 0051 differential executed exactly one root helper invocation and immediately returned to FullIO v19c Golden. The helper reached the existing bounded VFE1 Epoch0 timeout (`ETIMEDOUT`, surfaced as `Connection timed out` / `RUN_RC=1`), produced no QC10C buffer, and was not retried. RT-CDM reached FIFO sequence 17 without fault; IMX681 and CAMSS runtime PM returned to suspended. Golden return is verified with `saved_entry=sp11-audio-fullio-v19c`, empty `next_entry`, no camera modules loaded, and Golden cmdline identity.

0051 removed the Windows-unmatched Linux post-RUP_DONE write to CSID `REG_UPDATE_CMD +0x18` on the exact X1E80100 front-mode0 IPP path while retaining the software shadow clear and all RDI/non-front behavior. The exact installed Windows `qccamisp8380.sys` proof remains valid: Windows acknowledges the IPP IRQ but performs no corresponding RUP_DONE-conditioned `+0x18` write.

The hardware result is a clean negative differential. The first four Linux IPP IRQ/status-to-geometry pairs are byte-for-byte identical to 0050:

1. `0x00811dd0 / 0x00000f00`
2. `0x00600cc0 / 0x00000f00`
3. `0x00000cc0 / 0x00000f00`
4. `0x00004ee8 / 0x0a500f00`

Thus removing the post-RUP write does not improve first-Epoch geometry, remove bit14, advance VFE1 raw Epoch0, or produce output. Linux still matches Windows through the first meaningful RUP_DONE IRQ, then diverges by the immediately following Epoch0/1 IRQ: Windows checkpoint `0x00600228` is already `0x08700f00` = 3840x2160, while Linux `0x00600cc0` remains width-only and later completes as uncropped 3840x2640 with `ERROR_LINE_COUNT`.

Therefore the post-RUP `+0x18=0` write is a genuine Windows-parity defect but **not causal** for the vertical-crop failure. Keep the correction, but do not use it as the basis for another runtime. The next gate is static: distinguish active-update / event semantics capable of explaining why Windows has valid cropped geometry by first Epoch while Linux does not. The differing IRQ side bits (`EOF` class on Windows versus `SOL/EOL` class on Linux) must not be assumed causal until IRQ coalescing/clear timing is closed. No speculative crop-register write is justified.
