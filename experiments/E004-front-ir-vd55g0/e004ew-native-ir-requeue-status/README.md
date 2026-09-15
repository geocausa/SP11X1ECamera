# E004ew: native IR buffer reuse and applied status

Normal capture (test pattern disabled), unity digital gain and unchanged fixed
exposure/board mode. Request 16 frames through four MMAP buffers to exercise
buffer reuse beyond the first queue. One stream attempt, no same-boot retry.

Only driver addition: read-only sequential status snapshots after initialization,
after streaming starts and immediately before stopping. Read PIXEL_CLK (0x0040),
frame/context counters (0x004e–0x0057), applied exposure/gain (0x0064–0x0069),
and AE mode/status (0x0070–0x0071), using little-endian data. These are observations,
not an atomic association with a particular dequeued frame. They must succeed.
ST UM2829 Rev 2, section 19.1 documents the registers; section 13 distinguishes
timing pixel clock from the output link rate. Do not change timing metadata until
these actual values are available.

Require 16 full buffers with consecutive sequences, clean kernel, confirmed stop,
autosuspend, Golden return and retirement. Optical scene signal remains unproven.

Reference: https://www.st.com/resource/en/user_manual/um2829-how-to-integrate-and-configure-the-vd55g0-device-from-a-hardware-and-software-perspective-stmicroelectronics.pdf

## Result

PASS: 16 full frames, sequence 0–15, through four buffers; clean kernel,
confirmed stop and autosuspend, Golden return and retirement. Actual applied
exposure/gain are 100 lines / analogue code 0 / digital code 256. Sensor timing
clock is 137.6 MHz, consistent with approximately 58.65 fps at line length 1200
and frame length 1955. The currently advertised 84 MHz pixel rate is incorrect
for this fixed mode and must be corrected before application integration.
Normal pixels remain near black; this does not establish optical scene quality.
