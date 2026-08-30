# E003h 0049 runtime result — CSID1 line-count geometry localized

The authorized 0049 one-shot executed exactly once and returned to FullIO v19c Golden with no same-boot retry. The helper returned `ETIMEDOUT` waiting for VFE1 raw Epoch0, QC10C output remained absent, RT-CDM completed 17 FIFO BLs without fault, and the sensor/CAMSS runtime PM states returned to suspended before reboot.

The decisive new measurement was captured inside the existing CSID1 ISR at the exact IRQ carrying IPP bit14 `ERROR_LINE_COUNT`. The format-measure actual register was `0x0a500f00`, decoding to **3840x2640**, while the programmed expected register remains `0x08700f00`, decoding to **3840x2160**. Width matches exactly; the line count is 480 lines too large. Error-time HBI was `0x02c502c0`; VBI was `0x00000000`.

This does **not** justify changing the IMX681 mode. The accepted same-machine Windows oracle already proves the sensor transport itself is 3840x2640 RAW10 and Windows performs the 2640->2160 reduction in CSID1 IPP. Linux's crop register readbacks still match Windows (`HCROP=0x0eff0000`, `VCROP=0x086f0000`), and `CFG0=0x802b2000` has vertical crop enable set.

0049 also retains the 0048 historical CSID proof: OR=`0x00e15ff8`, last=`0x00004ee8`, count=4, including CAMIF SOF/EOF, CAMIF Epoch0/1, RUP_DONE and bit14. VFE1 raw BUS Epoch0 remains absent.

A correction to the prior Windows comparison is required: Windows `IPP_STATUS=0x00e11ff8` is a live snapshot, not a historical OR, and qccamisp services/clears CSID IRQs. Therefore Windows historical absence of bit14 is **not proven**. The prior static statement that Linux's transient bit14 is uniquely absent on Windows is superseded as a historical inference; the live Windows readback itself remains valid.

Next gate: capture same-machine Windows CSID1 IRQ history dynamically during a normal front-camera start. Break on the qccamisp IPP-error path only when bit14 is set; if it occurs, read `+0x388/+0x38c/+0x390/+0x394` at that exact interrupt. No further Linux runtime or programming delta is justified until this Windows history question is closed.

Fail-closed extractor SHA-256 `335ff1908298e54189bfbeafc69070223d8d94c68b22b33960c40e82ad44b962`; analysis SHA-256 `dd7860df3b63a78ca9af13b871a5b5e44d2e3aaef12da64f791094257fc4eac4`.
