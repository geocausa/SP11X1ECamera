# E003h Windows startup/priming interleave oracle

This same-machine Windows capture closes the remaining startup interleave needed by the bounded VFE1 PIX runner. The canonical first boot-start window is extracted from `E003H_STARTUP_PRIMING_INTERLEAVE_20260829.log`; markers after `CYCLE2_ARMED` are a non-canonical continuation window and are deliberately ignored by the fail-closed extractor.

Exact first-start order is:

`startup packet0 -> priming replay0 -> startup packet1 -> BUS static config -> BUS enable -> initial nine-client BUS addresses -> priming replay1 -> startup packet2 -> startup packet3 -> CSID1 start -> ISP_START_DONE`.

Combining this with the independently repeated priming/MIPI oracle gives:

`... -> ISP_START_DONE -> MIPI/CSIPHY start -> IMX681 stream-on -> priming replay2 -> priming replay3 -> first steady 0x958`.

This is ordering evidence only. It does not itself arm Linux PIX hardware.
