# E003h 0054 one-shot candidate — Windows-selected IMX681 mode2

Golden-safe bounded package for the first Linux PIX runtime using the same IMX681 resolution record selected by stock Windows Camera on this SP11.

Relative to consumed 0053, exactly three runtime assets change: `imx681.ko` switches from firmware record 0 (3840x2640@30) to the proven record 2 (3840x2160@30), `qcom-camss.ko` changes three front-path geometry eligibility checks from 2640 to 2160 with zero new MMIO writes, and `setup-pix-media.sh` requests 3840x2160. The helper, front-only DTB, oracle capsule and persistent RT-CDM observer are unchanged.

The sensor table equals all 68 address/value pairs captured from Windows and differs from prior Linux mode0 in exactly seven values. CSID programming values remain unchanged; the already-derived Windows CSID configuration expects 3840x2160.

Installation cannot arm the boot. Runtime is not authorized by this package and requires a separately committed authorization. Any authorized run permits exactly one helper invocation, refuses same-boot retry when the RUN log exists, requires the persistent RT-CDM observer, archives the result and immediately reboots to Golden.

## Consumed runtime result

The single authorized run has completed and authorization is consumed. The mode2 correction removed the CSID1 `ERROR_LINE_COUNT` fault and changed the first completed measured frame from 3840x2640 to exact 3840x2160, with subsequent healthy 2160 samples. VFE1 Epoch0 still times out and QC10C remains absent. See `RESULT.md` and accepted `runtime-0054-analysis.json`.
