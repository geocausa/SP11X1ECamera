# E002i-A result — ACCEPTED

The exact accepted E002h-r1 payload streamed 16 consecutive 4076x2806 packed-GRBG10 frames to `/dev/null` through the native OV13858 -> CSIPHY1 -> CSID0 -> VFE0 RDI0 path.

- STREAMON returned success;
- sequences were exactly 0 through 15;
- every buffer reported `bytesused=14321824`;
- mean EOF timestamp delta was ~33.385 ms (~29.95 fps), with no missing sequence;
- STREAM_RC=0;
- sensor returned to runtime `suspended`, usage 0;
- MCLK1, CSIPHY1 and CSI1 timer clocks returned to enable count 0;
- no new Oops/paging/internal errors were observed.

E002i-A short-stream stability is accepted. E002i-B may now vary only the standard V4L2 exposure control, with analogue/digital gain and all transport parameters fixed.
