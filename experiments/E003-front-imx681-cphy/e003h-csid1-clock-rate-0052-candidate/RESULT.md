# E003h 0052 result — X1E CSID clock correction fixes HBI, not crop

The single authorized 0052 diagnostic executed exactly one root helper invocation and immediately returned to FullIO v19c Golden. The helper reached the existing bounded VFE1 Epoch0 timeout (`ETIMEDOUT`, surfaced as `Connection timed out` / `RUN_RC=1`), produced no QC10C buffer, and was not retried. RT-CDM reached FIFO sequence 17 without fault; IMX681 and CAMSS runtime PM returned to suspended.

0052 changed only the exact X1E80100 front route's `csid` and `csid_csiphy_rx` clock requests from Linux's generic 300 MHz first-table selection to the existing link-derived 400 MHz selection. The result proves that clock bug was real: error-time HBI changed from the 0051 value `0x02c502c0` to `0x03b203ad`, exactly matching the bounded Windows normal HBI sample `0x03b203ad`.

The vertical-crop failure is nevertheless unchanged. The complete ordered CSID sequence remains `00811dd0/00000f00 -> 00600cc0/00000f00 -> 00000cc0/00000f00 -> 00004ee8/0a500f00`; first completed EOF remains 3840x2640 with `ERROR_LINE_COUNT`, despite crop readback `0x0eff0000/0x086f0000` and expected frame `0x08700f00`. VFE1 raw Epoch0 does not advance and QC10C remains absent.

Therefore keep the 0052 X1E clock correction as a real timing-domain fix, but retire CSID clock rate as the crop cause. Direct Windows 400 MHz voting is still not claimed. The next gate is static: close CSID680 active vertical-crop/latch semantics, including IPP CFG0/VCROP/CTRL ordering, RUP/AUP/update commands, and LUT/active-bank selection. No further runtime is authorized until a concrete active-bank/update/lifecycle delta is proven.
