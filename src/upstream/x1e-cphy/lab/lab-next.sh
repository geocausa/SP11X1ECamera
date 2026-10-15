#!/bin/sh
# sp11-next-lab boot only: load the upstream (linux-next) CSI2 PHY driver and CAMSS (test builds)
# plus an upstream-candidate sensor driver, then capture raw RDI frames.
# Usage: lab-next.sh rear|front <out-dir> [exposure] [again]   (EXTRA/PRE: more sensor controls)
WHICH=$1; O=$2; EXP=${3:-2000}; AG=${4:-256}
T=/root/imx681-test
mkdir -p $O; exec > $O/log.txt 2>&1
set -x
grep -q sp11-next-lab /proc/cmdline || { echo 'not the next lab boot'; exit 1; }
pkill v4l2-ctl; sleep 1
rmmod ov13858 imx681 qcom_camss phy_qcom_mipi_csi2 2>/dev/null
for m in i2c_qcom_cci mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg videobuf2_vmalloc v4l2_cci; do modprobe $m; done
N0=$(dmesg | wc -l)
insmod $T/next/phy/phy-qcom-mipi-csi2.ko
sleep 1
insmod $T/next/camss/qcom-camss.ko
[ -n "$BOTH" ] && { insmod $T/ovmod/ov13858.ko; insmod $T/mod/imx681.ko; }
if [ $WHICH = rear ]; then
  insmod $T/ovmod/ov13858.ko; SN='ov13858 3-0010'; PHY=msm_csiphy1; CSID=msm_csid0; RDI=msm_vfe0_rdi0; VID=msm_vfe0_video0
  W=4224; H=3136; F=SGRBG10_1X10; PF=pgAA; BPL=5280
else
  insmod $T/mod/imx681.ko; SN='imx681 1-0010'; PHY=msm_csiphy2; CSID=msm_csid1; RDI=msm_vfe1_rdi0; VID=msm_vfe1_video0
  W=3844; H=2640; F=SRGGB10_1X10; PF=pRAA; BPL=4816
fi
sleep 3
ls /sys/bus/platform/drivers/qcom-mipi-csi2-phy/ 2>&1
M=$(for m in /dev/media*; do media-ctl -d $m -p 2>/dev/null | grep -q $CSID && echo $m; done | head -1)
media-ctl -d $M -p | grep -E '^- entity' | head -40
S=$(media-ctl -d $M -e "$SN")
V=$(media-ctl -d $M -e $VID)
media-ctl -d $M -l "\"$PHY\":1->\"$CSID\":0[1], \"$CSID\":1->\"$RDI\":0[1]"
for e in "\"$SN\":0" "\"$PHY\":0" "\"$PHY\":1" "\"$CSID\":0" "\"$CSID\":1" "\"$RDI\":0" "\"$RDI\":1"; do
  media-ctl -d $M -V "$e[fmt:$F/${W}x$H field:none]"
done
media-ctl -d $M -p | grep -A6 -E "entity.*($SN|$PHY |$CSID |$RDI )" | grep -E 'entity|fmt|ENABLED'
v4l2-ctl -d $V --set-fmt-video=width=$W,height=$H,pixelformat=$PF
v4l2-ctl -d $V --get-fmt-video | grep -E 'Width|Bytes|Size'
[ -n "$PRE" ] && v4l2-ctl -d $S --set-ctrl $PRE
v4l2-ctl -d $S --set-ctrl exposure=$EXP,analogue_gain=$AG${EXTRA:+,$EXTRA}
timeout 12 v4l2-ctl -d $V --stream-mmap=4 --stream-skip=15 --stream-count=3 --stream-to=$O/raw.bin
echo "capture rc=$?"
ls -la $O/raw.bin
timeout 8 v4l2-ctl -d $V --stream-mmap=4 --stream-count=60 2>&1 | tail -2
echo "W=$W H=$H BPL=$BPL"
dmesg | tail -n +$N0 | grep -v -E '^\[ *[0-9.]+\]  |x[0-9]+ ?:|Modules linked|Tainted|Hardware name|pstate|pc :|lr :|sp :|end trace' | tail -40
