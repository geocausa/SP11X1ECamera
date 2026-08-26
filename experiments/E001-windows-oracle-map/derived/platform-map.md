# E001 static oracle — common camera platform

The local Surface camera platform extension exposes AeoB platform files in addition to the per-sensor resources.

## Performance table
`CAMP_PERF_MSHW0495.bin` decodes to named P-state sets including:
- `cam_cc_cci_0_clk`: 37.5 MHz
- `cam_cc_cci_1_clk`: 37.5 MHz
- NRT and real-time/compressed camera bandwidth tables
- `cam_cc_camnoc_axi_rt_clk`: up to 400 MHz
- `cam_cc_camnoc_axi_nrt_clk`: up to 400 MHz
- a `CAM_PRLD` state set

This proves Windows has both CCI0 and CCI1 platform clocks available but does **not** by itself assign an individual sensor to either CCI controller.

## Platform config / privacy LED
`CAMP_PCFG_MSHW0495.bin` and `CAMP_PRLD_MSHW0495.bin` are valid AeoB packages but contain integer-only structures. They have been decoded locally; field semantics are not named in the package, so E001 does not guess their meaning.

The selected local `CAMP_RES_MSHW0495` differs from the public Surface corpus, so platform-level values must remain tied to the local Windows package revision.
