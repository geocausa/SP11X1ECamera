# E002h preflight — first controlled rear stream

## Question
Can the accepted native OV13858 Surface mode produce one RAW10 frame through unmodified X1E CAMSS using the existing default path?

## One new runtime variable
E002h adds only an experiment-only DT permission boolean:

`microsoft,e002h-allow-stream`

The existing `microsoft,e002e-no-stream` safety property remains present. The E002h driver changes only the gate so streaming is allowed when both the safety baseline and the explicit E002h permission are present.

No accepted camera electrical or transport parameters change:

- 4076x2806 Surface mode0;
- four-lane D-PHY;
- LINK_FREQ 592800000 Hz;
- VT PIXEL_RATE 432732960 Hz;
- HBLANK 412 / VBLANK 408;
- GPIO97 MCLK1, GPIO110 reset;
- four proven rear rails and order;
- CSIPHY1 graph;
- upstream X1E CSIPHY/CSID/VFE code.

## Proven native route
`ov13858 -> msm_csiphy1 -> msm_csid0 -> msm_vfe0_rdi0 -> /dev/video0`

The default CAMSS links already select this route. Active no-stream negotiation on E002g proved SGRBG10 4076x2806 across all subdevs and packed GRBG10 (`pgAA`) on `/dev/video0` without electrical activity.

## Receiver audit
Both X1E CSIPHY and CSID obtain link frequency through the standard sensor V4L2 LINK_FREQ control. At 592.8 MHz the requested rates fit the existing X1E clock tables; integrated X1E D-PHY settle timing is calculated natively from that link frequency.

## Capture contract
Configure the accepted active format chain, then request exactly one mmap frame from `/dev/video0` with packed GRBG10 4076x2806. Bound userspace with `timeout`; success must produce a non-empty frame and normal STREAMOFF/close teardown. On timeout/failure, close/kill the capture process and inspect clocks, runtime PM and dmesg before any retry.

Do not alter media links, sensor controls, link rate, PLL, rails, reset, CAMSS source, or Golden.
