#!/bin/sh
# sp11-imx681-lab boot (nothing camera loaded yet). VD55G0 0x0329 test for Sergey:
# isl_mode 0 = never write (our fix), 1 = at each stream start (Peter v2), 2 = once per power-on.
O=${OUT:-/root/imx681-test/irISL}; rm -rf $O; mkdir -p $O; exec > $O/log.txt 2>&1
D=/var/lib/sp11-camera-daily2; T=/root/imx681-test; P=/sys/module/vd55g1/parameters
grep -q 'sp11_entry=7.1.5-sp11-imx681-lab' /proc/cmdline || { echo 'not a lab boot'; exit 1; }
lsmod | grep -q '^vd55g1' && { echo 'vd55g1 already loaded; reboot to the lab entry first'; exit 1; }
for m in i2c_qcom_cci mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg videobuf2_vmalloc v4l2_cci; do modprobe $m; done
insmod $D/modules/qcom-camss.ko $(cat $D/camss-params.txt)
insmod $D/modules/imx681.ko
insmod $T/ovmod/ov13858.ko
insmod $T/vdisl/vd55g1.ko
sleep 3
M=$(for m in /dev/media*; do media-ctl -d $m -p 2>/dev/null | grep -q msm_csid0 && echo $m; done | head -1)
SN=$(media-ctl -d $M -p | sed -n 's/^- entity [0-9]*: \(vd55g[^(]*\) (.*/\1/p' | head -1 | sed 's/ *$//'); echo "sensor=$SN"
S=$(media-ctl -d $M -e "$SN"); V=$(media-ctl -d $M -e msm_vfe0_video0)
W=644; H=604; F=Y10_1X10
media-ctl -d $M -l '"msm_csiphy0":1->"msm_csid0":0[1], "msm_csid0":1->"msm_vfe0_rdi0":0[1]'
for e in "\"$SN\":0" '"msm_csiphy0":0' '"msm_csiphy0":1' '"msm_csid0":0' '"msm_csid0":1' '"msm_vfe0_rdi0":0' '"msm_vfe0_rdi0":1'; do
  media-ctl -d $M -V "$e[fmt:$F/${W}x$H field:none]"
done
v4l2-ctl -d $V --set-fmt-video=width=$W,height=$H,pixelformat=Y10P
v4l2-ctl -d $S --set-ctrl exposure=500
N0=$(dmesg | wc -l)
for run in 0a 1a 2a 0b 1b 2b; do
  mode=${run%?}
  echo "===== run=$run isl_mode=$mode"
  sleep 6   # runtime PM powers the sensor off, so the next stream starts from a fresh power-on
  echo $mode > $P/isl_mode
  timeout -k 2 8 v4l2-ctl -d $V --stream-mmap=4 --stream-skip=5 --stream-count=3 --stream-to=$O/$run.raw
  echo "capture rc=$? bytes=$(stat -c %s $O/$run.raw 2>/dev/null)"
  dmesg | tail -n +$N0 | grep -E 'SP11ISL|vd55g1|csid|vfe' | tail -12
  N0=$(dmesg | wc -l)
done
echo done
