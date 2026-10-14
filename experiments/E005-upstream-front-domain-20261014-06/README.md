# Fresh06 corrected genpd observer and sensor-domain teardown

Source29 DTB unchanged from05. The retained05 summary and actual kernel
formatter prove dev_name is printed; corrected helper validates one exact
sensor name and suspended status under one TOP header. No other behavior
change.05 is consumed/retired, it stopped before unload. No retry of05.

Fresh06 uses the same CAMSS-first unload order and strict post-unload kernel
log guard. No buffers, streaming, pixels, new firmware or OS sleep. Pinned
existing kernel/initrd/module artifacts reused;180s independent return and
ExecStopPost preserve Golden. Source/helper/units pinned before one-use arm.
