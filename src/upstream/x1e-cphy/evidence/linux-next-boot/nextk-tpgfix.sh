#!/bin/sh
# sp11-next-kernel boot: verify the camss TPG menu skip-mask fix (no oops on -m, rmmod works)
O=/root/imx681-test/nxk/tpgfix; rm -rf $O; mkdir -p $O
uname -a > $O/uname.txt; modinfo -F srcversion qcom_camss >> $O/uname.txt
for m in i2c_qcom_cci v4l2_cci phy_qcom_mipi_csi2 qcom_camss ov13858 imx681; do modprobe $m; done; sleep 8
for n in /sys/class/video4linux/v4l-subdev*; do
  if grep -q msm_tpg $n/name; then echo /dev/$(basename $n) $(cat $n/name) >> $O/tpgdevs.txt; fi
done
D=$(head -1 $O/tpgdevs.txt | cut -d' ' -f1)
v4l2-ctl -d $D --list-ctrls-menus > $O/menus.txt 2>&1
for v in 0 1 2 3 4 5 6 7 8 9 10; do echo "set $v:" $(v4l2-ctl -d $D -c test_pattern=$v 2>&1; echo rc=$?) >> $O/sctrl.txt; done
v4l2-ctl -d $D -c test_pattern=0 >> $O/sctrl.txt 2>&1
timeout 90 v4l2-compliance -m /dev/media0 > $O/compliance.txt 2>&1
grep -E '^Total for' $O/compliance.txt > $O/totals.txt
N0=$(dmesg | wc -l)
rmmod imx681 ov13858 2>>$O/rmmod.txt
(rmmod qcom_camss 2>>$O/rmmod.txt; echo "rmmod camss rc=$?" >> $O/rmmod.txt) &
sleep 20
ps -eo pid,stat,cmd | grep -E 'rmmod' | grep -v grep >> $O/rmmod.txt || true
for p in $(pgrep -x rmmod); do cat /proc/$p/stack >> $O/rmmod.txt; done
modprobe qcom_camss 2>>$O/rmmod.txt; sleep 5; echo "reload: $(ls /dev/media* 2>&1)" >> $O/rmmod.txt
dmesg | tail -n +$N0 > $O/dmesg.txt
dmesg | grep -iE 'oops|BUG|Unable to handle|Call trace' > $O/oops.txt || true
journalctl -b > $O/journal.txt 2>&1
echo done > $O/done; sync
