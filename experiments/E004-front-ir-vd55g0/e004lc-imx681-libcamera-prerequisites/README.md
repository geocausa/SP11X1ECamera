# E004lc IMX681 libcamera prerequisites

## Outcome
Clean upstream libcamera v0.7.0 base b7854fd07d42168f099b5ce30d1702e0e0875bf5 plus the independent IMX681 gain helper built all 359 Ninja targets. Factory/gain operating points, Bayer format and pixel format tests passed (3/3). The existing dirty reference checkout and installed libcamera were untouched. Build configuration is in SETUP.txt; no camera or system installation occurred.

The helper is in src/front-imx681/libcamera. It expresses the previously verified analogue-gain law, with no invented black level. This is a prerequisite, not a working libcamera camera stack.

## Timing gate
The driver lacks mandatory HBLANK and PIXEL_RATE. Existing E003i CQ evidence resolves HBLANK=2912 and the exposure/VT rate=719898240 Hz. The 548570000 Hz mode field is output-clock metadata and is not correct for line/exposure duration.

Both CAMSS VFE clock selection and subsequent rate checking consume PIXEL_RATE. With the correct VT rate, PIX needs 755893152 Hz after the existing 5 percent margin, exceeding the X1E maximum of 727000000 Hz. RAW10 RDI instead selects 345600000 Hz, whereas missing PIXEL_RATE currently falls back to 727000000 Hz. Thus exposing mandatory metadata changes hardware clocking and can reject the accepted PIX route.

The exact kernel v4l2_get_link_freq implementation prefers get_mbus_config.link_freq, so IMX681's explicit 1200000000 Hz link remains authoritative. Do not replace it with a guessed rate or bypass libcamera validation.

The hardware-free verify-clock-consumer.py compiles both actual accepted CAMSS C functions against clock stubs. Four selection cases and two rate-check cases pass, reproducing the rejection without camera access. This tests control flow, not physical clock sufficiency. The harness initially needed struct-name and newline fixes; final CLOCK-TESTS.txt records the passing run.

Next: resolve CAMSS transport-bandwidth versus sensor-array timing semantics, with an independently checked C-PHY calculation and coverage of both set/check clock paths, before creating a new kernel runtime candidate. No kernel patch or physical test is admitted by this source-only result.

## FPS interpretation
The archived Windows internal table includes a 3840x2160@60 mode (line 5408, frame 2218). That is static capability evidence, not a live validated 60 fps mode or ordinary application format. E004ky found only 30 fps advertised through VideoRecord and observed about 15 fps in its uncontrolled scene. Neither observation establishes a hardware ceiling.

## Safety and remaining work
Golden boot efce8736-4641-48b0-929c-f511e923e571 was unchanged, with no camera modules/devices/processes or pending boot. No optical data was recorded. E004la remains the latest physical acceptance. Sensor/publisher restart, suspend, persistent production lifecycle, calibrated image quality and front QC10C/Windows ISP parity remain open.

Archived build/test logs have terminal carriage returns and trailing whitespace normalized; original outputs remain in the temporary build directory.
