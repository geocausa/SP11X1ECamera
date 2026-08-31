# E003h first complete EOF geometry boundary

0050/0051 previously described the Windows/Linux geometry divergence as occurring "by first Epoch". That phrasing compared unlike sampling points. The Windows checkpoint status `0x00600228` already contains `CAMIF_EOF`, while Linux's first Epoch status `0x00600cc0` does not. Both systems show width-only/incomplete height before EOF.

The fail-closed extractor pins the exact installed qccamisp binary, Windows mask/start oracle, preserved Windows geometry checkpoint, Linux 0051 runtime analysis and exact Linux CSID680 source. It also verifies qccamisp reads IPP status and later clears that complete snapshot, so unmasked side bits may co-reside according to ISR/clear timing and are not a strict event-order oracle.

The corrected boundary is the **first completed EOF/frame-size measurement**: Windows is 3840x2160; Linux is 3840x2640 and raises `ERROR_LINE_COUNT`. The crop failure remains real, but the pre-EOF Epoch geometry comparison is superseded. No new register write follows from this correction.
