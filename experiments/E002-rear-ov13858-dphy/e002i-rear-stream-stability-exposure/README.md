# E002i — rear stream stability and standard exposure response

E002i uses the exact accepted E002h-r1 payload without kernel, initrd, module, DT, graph, mode, clock, rail or register-table changes.

## E002i-A — short stream stability

Configure the accepted native route at 4076x2806 SGRBG10 / packed GRBG10 and stream exactly 16 frames to `/dev/null`.

Acceptance:

- STREAMON succeeds;
- sequences are monotonic 0..15;
- all 16 frames report full `bytesused=14321824`;
- timestamps are monotonic and cadence is compatible with ~30 fps;
- normal close/STREAMOFF returns sensor PM usage to 0 and MCLK1/CSIPHY1 clocks to 0;
- no new kernel warnings/Oops/errors;
- Wi-Fi and audio remain healthy.

## E002i-B — exposure response

Only after E002i-A passes, use the native OV13858 V4L2 exposure control while keeping analogue/digital gain and every transport setting fixed. Capture one local-only frame at a low exposure and one at a high exposure, and compare decoded RAW10 statistics. Do not change mode/PLL/link frequency/graph.
