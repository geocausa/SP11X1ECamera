# E003i-AN — bounded live AM IMX681 control runtime

Status: **CONSUMED — live AM sensor transaction PASS; parent TL_BG/3A audit race FAIL; Golden return PASS.**

AN is not an AL retry. AL was consumed before STREAMON after proving privileged sensor discovery and showing that AJ's old four-control cluster clobbered requested exposure 3500 back to 3546. AM closes that root cause offline by keeping VBLANK standalone and clustering exposure + analogue gain + global digital gain with exposure as master.

AN reuses the exact proven AI front-only DTB, Z/Y CAMSS, six-frame helper, template-free R4 and deadline-hardened R5/R6 producer. The only hardware asset substitution is AM `imx681.ko` SHA256 `c2b63b747176d3e8a7f8ee658833e0c1806fad9e03185840208ff5e466ce6ba8`.

Before STREAMON AN must dynamically discover the sensor subdev as root and cache exposure 3500, analogue code 0x040 and global digital Q8.8 0x0110 while VBLANK remains 1394/FLL 3554. At stream-on, AM must restore mode2 and emit the exact group-held success transaction `AM request controls: FLL=3554 exposure=3500 again=0x040 dgain=0x0110 ret=0` before MODE_SELECT=1. Then the unchanged six-frame/R5/R6 path must pass and the machine must return Golden. No same-boot retry is permitted.

## AN consumed result

AN cached the requested controls exactly and reached STREAMON. AM emitted the exact group-held transaction `FLL=3554 exposure=3500 again=0x040 dgain=0x0110 ret=0` twice during control restore, proving the Linux sensor-control write path live. The deadline-hardened producer also acquired paired G1-G3, derived the changed-state Lux/CCT, and successfully submitted R5 `1050e1e8…fe18b` and R6 `abcf96db…2b88e`.

The parent audit then pinned at frame 0 after reading TL_BG generation/source/slot `1/1/0` and observing a different identity in its subsequent one-shot 3A read. This does not invalidate the producer pair: the kernel controls are separately locked volatile **latest** snapshots, and the runner publishes TL_BG immediately before 3A for each identical source sequence/slot. A publication boundary can therefore land between the parent's old TL_BG-first and 3A-second reads. The live producer already avoids this with a retrying 3A-first then TL_BG matching loop.

AN was not retried. It was archived while pinned and rebooted directly to Golden. Golden return passed with empty `next_entry` and no camera modules. The sensor-control obstacle is live-closed; the remaining AN failure is the redundant parent audit reader. AO will change only that helper logic.
