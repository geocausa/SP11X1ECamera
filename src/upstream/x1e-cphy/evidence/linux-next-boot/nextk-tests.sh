#!/bin/sh
# sp11-next-kernel boot (real linux-next kernel): front C-PHY test pattern, front scene, rear D-PHY.
T=/root/imx681-test; O=$T/nxk; rm -rf $O; mkdir -p $O; export BOTH=1
uname -a > $O/uname.txt; cat /proc/cmdline >> $O/uname.txt
EXTRA=test_pattern=2 $T/lab-nextk.sh front $O/front-tp 1500 0
md5sum $O/front-tp/raw.bin $T/nxF/raw.bin > $O/md5.txt
$T/lab-nextk.sh front $O/front 2000 256
$T/lab-nextk.sh rear $O/rear 2000 256
dmesg > $O/dmesg.txt
journalctl -b > $O/journal.txt 2>&1
echo done > $O/done
sync
# no network on this kernel: go back to the default boot by itself
systemctl reboot
