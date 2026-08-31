# E003h 0050 — ordered first-IPP geometry result

The single authorized 0050 diagnostic executed exactly one root helper invocation and immediately returned to FullIO v19c Golden. The helper reached the existing bounded VFE1 Epoch0 timeout (`ETIMEDOUT`, surfaced by sysfs as `Connection timed out` / `RUN_RC=1`), returned no QC10C buffer, and was not retried. RT-CDM reached FIFO sequence 17 without fault and stopped cleanly; IMX681 and CAMSS runtime PM returned to suspended. Golden return is verified with `saved_entry=sp11-audio-fullio-v19c`, empty `next_entry`, no camera modules loaded, and Golden cmdline identity.

0050 resolves the startup geometry ordering. Linux CSID1 recorded exactly four nonzero IPP IRQs before timeout:

1. `0x00811dd0 / 0x00000f00`: includes `CAMIF_SOF` and `RUP_DONE`; measured width is 3840 and height is not yet complete.
2. `0x00600cc0 / 0x00000f00`: includes `CAMIF_EPOCH0|CAMIF_EPOCH1`; measured width remains 3840 and height is still zero.
3. `0x00000cc0 / 0x00000f00`: height is still zero.
4. `0x00004ee8 / 0x0a500f00`: includes `CAMIF_EOF` and `ERROR_LINE_COUNT`; actual geometry is 3840x2640.

The preserved Windows checkpoint reports the same first meaningful status `0x00811dd0` with width initialized and height incomplete. The very next Windows Epoch-bearing IRQ is `0x00600228`, where actual is already `0x08700f00` = 3840x2160. Thus the first proven divergence is **after the matching RUP_DONE IRQ and by the immediately following Epoch0/1 IRQ**. Windows has activated the vertical crop by first Epoch; Linux has not. Linux later measures the uncropped 2640-line frame and raises bit14.

All existing parity values remain intact at timeout: crop readback `0x0eff0000/0x086f0000`, expected format `0x08700f00`, CFG `0x802b2000/0x7241`, clean CSI ingress of 37,016 packets with zero ECC/CRC, and VFE1 raw BUS Epoch0 still absent. Sensor timing/programming remains disqualified as a delta, and no speculative crop-register write is justified.

The Windows raw first-IRQ KD file is still not locally recovered; the comparison above is explicitly bound to the committed preservation checkpoint and retains that fail-closed provenance warning. Do not reconstruct substitute raw evidence.

Runtime extractor SHA-256 `7c736bfb37d95ea252cbcc9734321e37df396c6915423c2aea3374d22f70917c`; analysis SHA-256 `bc8c2fd7033121592e540e3eedde134e56cab6d2525526f7771a74ec7b424459`. Next gate: statically audit the exact RUP_DONE-to-first-Epoch ownership transition, especially any Linux-only write to CSID `REG_UPDATE_CMD +0x18`, before another runtime or programming delta.
