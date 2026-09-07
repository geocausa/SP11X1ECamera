# E003i-AL — bounded live AJ IMX681 control runtime, privileged discovery

Status: **READY / UNEXECUTED — fresh one-shot after AK pre-stream permission failure.**

AL is not an AK retry. It has a distinct boot entry and one-shot lifecycle. AK was consumed without STREAMON because its graph setup ran as root but its subsequent `media-ctl -e` lookup ran unprivileged and received `-13 EACCES`. AK returned Golden cleanly and remains permanently consumed.

AL preserves the exact proven AI transport and AJ sensor module. Its only functional packaging correction is to execute sensor entity lookup and V4L2 subdevice control access with passwordless root, matching the permissions already required by the media graph setup. The sensor entity is still discovered dynamically; no CCI adapter number is hard-coded.

Before STREAMON AL must enumerate `vertical_blanking`, `exposure`, `analogue_gain`, and `digital_gain`, then cache the same low-risk non-default request while the sensor is runtime-suspended: vblank `1394` (FLL `3554`), exposure `3500`, analogue code `0x040`, global digital Q8.8 `0x0110`.

At STREAMON, AJ must restore mode2 and publish that cached cluster under group hold before `MODE_SELECT=1`. With AJ dynamic debug enabled, acceptance requires the exact hardware-success line:

`AJ request controls: FLL=3554 exposure=3500 again=0x040 dgain=0x0110 ret=0`

The unchanged AI six-frame/R5/R6 helper must then close normally with QC10C sequences 0..5, paired TL_BG+3A generations 1..6, successful live R5 and R6 submissions, no kernel-health regression, no same-boot retry, and mandatory Golden return.
