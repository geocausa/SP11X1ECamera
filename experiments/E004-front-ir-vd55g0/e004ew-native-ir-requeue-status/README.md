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
