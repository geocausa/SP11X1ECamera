# E002i-B result — ACCEPTED

With the accepted 4076x2806 RAW10 transport unchanged, only standard V4L2 exposure was varied from 100 to 3000 lines. Analogue gain remained 128, digital gain 1024, VBLANK 408 and test pattern disabled.

Both one-frame captures STREAMON'd and dequeued full 14,321,824-byte frames, with clean runtime-PM/clock teardown between captures.

Decoded RAW10 response:

- exposure 100: mean 64.3415, stdev 0.7728;
- exposure 3000: mean 65.2285, stdev 0.9346;
- mean delta +0.8870 counts;
- central-region mean 64.3500 -> 65.3988;
- all four Bayer parity means increased;
- 64.47% of pixels increased, 8.28% decreased.

The scene is very dark and signal sits close to the sensor black pedestal, so the absolute brightness response is intentionally modest. Across ~11.4 million pixels the direction is coherent and establishes that the standard V4L2 exposure path affects captured sensor data.

Raw frames remain local-only; only hashes/statistics are committed.
