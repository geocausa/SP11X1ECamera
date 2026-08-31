# Windows IMX681 six-mode correction

The exact current Surface IMX681 module does not contain only one resolution. It contains six 252-byte `resolutionData` records. The earlier clean-room mode0 extractor intentionally followed only record 0 and therefore could not prove which record Windows selected.

The critical correction is record 2: **3840x2160 @ 30 fps**, with line length **6752**, frame length **3554**, and output pixel clock **548.57 MHz** — exactly the timing previously used to argue that Windows matched Linux's 3840x2640 record 0. Record 2 programs sensor output/digital-crop size `0x0f00 x 0x0870` (3840x2160).

Therefore timing parity alone does not identify Windows's selected sensor mode. Existing Windows CSID completed-frame geometry (3840x2160) is consistent with record 2, but record-2 selection is not yet proven. No Linux mode change is authorized. The next oracle must capture the same-machine Windows `CSLPacketOpcodesSensorCrop` register pairs or equivalent live IMX681 output-size registers.
