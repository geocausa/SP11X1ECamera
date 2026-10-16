#!/bin/sh
# sp11-next-lab boot (DTB has all three sensors): C-PHY v2 test run.
T=/root/imx681-test; O=$T/nx2; rm -rf $O; mkdir -p $O
export ALL=1
EXTRA=test_pattern=2 $T/lab-next2.sh front $O/front-tp 1500 0
md5sum $O/front-tp/raw.bin $T/nxF/raw.bin > $O/md5.txt
$T/lab-next2.sh front $O/front 2000 256
$T/lab-next2.sh rear $O/rear 2000 256
echo done > $O/done
