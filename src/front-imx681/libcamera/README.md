# IMX681 libcamera prerequisites

Gain helper patch targets upstream libcamera v0.7.0 commit b7854fd07d42168f099b5ce30d1702e0e0875bf5. Independently derived IMX681 gain encoding is verified in E003i AJ/CQ; raw code0..960 means1x..16x. No guessed black level, board alias or tuning data. Compile/factory/known-operating-point test included. Not installed or submitted upstream.

The current sensor driver lacks mandatory HBLANK and PIXEL_RATE controls. HBLANK is2912 from verified6752-line-length minus3840 width. E003i CQ proves Windows exposure timing uses719898240Hz, distinct from548570000Hz CSI output metadata. Adding these controls also affects CAMSS clock and link-frequency consumers; requires a reviewed kernel candidate and a fresh physical validation. Do not bypass libcamera sensor validation or expose the transport clock as exposure timing.
