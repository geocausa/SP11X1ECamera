# E003i-AN — bounded live AM IMX681 control runtime

Status: **READY / UNEXECUTED — fresh one-shot after AL exposed AJ's cluster-cache bug.**

AN is not an AL retry. AL was consumed before STREAMON after proving privileged sensor discovery and showing that AJ's old four-control cluster clobbered requested exposure 3500 back to 3546. AM closes that root cause offline by keeping VBLANK standalone and clustering exposure + analogue gain + global digital gain with exposure as master.

AN reuses the exact proven AI front-only DTB, Z/Y CAMSS, six-frame helper, template-free R4 and deadline-hardened R5/R6 producer. The only hardware asset substitution is AM `imx681.ko` SHA256 `c2b63b747176d3e8a7f8ee658833e0c1806fad9e03185840208ff5e466ce6ba8`.

Before STREAMON AN must dynamically discover the sensor subdev as root and cache exposure 3500, analogue code 0x040 and global digital Q8.8 0x0110 while VBLANK remains 1394/FLL 3554. At stream-on, AM must restore mode2 and emit the exact group-held success transaction `AM request controls: FLL=3554 exposure=3500 again=0x040 dgain=0x0110 ret=0` before MODE_SELECT=1. Then the unchanged six-frame/R5/R6 path must pass and the machine must return Golden. No same-boot retry is permitted.
