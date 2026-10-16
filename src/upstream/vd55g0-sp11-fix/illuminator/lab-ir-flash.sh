#!/bin/sh
# sp11-ir-flash-lab boot only. Peter's vd55g1 (+our fix) + patched leds-qcom-flash, IR LED in hardware strobe
# from sensor GPIO1. Safety: DT caps 200 mA total / 10 ms per pulse; manual exposure ~1 ms (~6% duty at 60 fps);
# LED armed only around short captures and always disarmed on exit.
# Usage: lab-ir-flash.sh <out-dir> [exposure-lines] [analogue-gain list]
O=$1; EXP=${2:-117}; GAINS=${3:-"0 16"}
D=/var/lib/sp11-camera-daily2; T=/root/imx681-test
mkdir -p $O; exec > $O/log.txt 2>&1
set -x
grep -q sp11-ir-flash-lab /proc/cmdline || { echo 'not the flash lab boot'; exit 1; }
for m in i2c_qcom_cci mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg videobuf2_vmalloc v4l2_cci led_class_flash v4l2_flash_led_class; do modprobe $m; done
N0=$(dmesg | wc -l)
insmod $T/flashmod/leds-qcom-flash.ko
sleep 1; ls /sys/class/leds/
insmod $D/modules/qcom-camss.ko $(cat $D/camss-params.txt)
insmod $D/modules/imx681.ko
insmod $T/ovmod/ov13858.ko
insmod $T/vdflash/vd55g1.ko
sleep 3
M=$(for m in /dev/media*; do media-ctl -d $m -p 2>/dev/null | grep -q msm_csid0 && echo $m; done | head -1)
SN=$(media-ctl -d $M -p | sed -n 's/^- entity [0-9]*: \(vd55g[^(]*\) (.*/\1/p' | head -1 | sed 's/ *$//')
FN=$(media-ctl -d $M -p | sed -n 's/^- entity [0-9]*: \([^(]*illuminator[^(]*\|[^(]*flash[^(]*\) (.*/\1/p' | head -1 | sed 's/ *$//')
echo "sensor=$SN flash=$FN"
S=$(media-ctl -d $M -e "$SN"); V=$(media-ctl -d $M -e msm_vfe0_video0)
[ -n "$FN" ] && FL=$(media-ctl -d $M -e "$FN")
[ -n "$FL" ] || { echo 'no flash subdev in the media graph'; dmesg | tail -n +$N0 | grep -iE 'flash|led|vd55' | tail; exit 1; }
name() { v4l2-ctl -d $1 -l | awk -v id=$2 '$2==id {print $1}'; }
LM=$(name $FL 0x009c0901); SS=$(name $FL 0x009c0902); TO=$(name $FL 0x009c0906); IN=$(name $FL 0x009c0907); FA=$(name $FL 0x009c090a)
SLM=$(name $S 0x009c0901); AE=$(name $S 0x009a0901)
echo "ctrls flash: $LM $SS $TO $IN $FA sensor: $SLM $AE"
disarm() { v4l2-ctl -d $FL --set-ctrl $SS=0; v4l2-ctl -d $FL --set-ctrl $LM=0; v4l2-ctl -d $S --set-ctrl $SLM=0; }
trap disarm EXIT INT TERM
v4l2-ctl -d $FL -l
W=644; H=604; F=Y10_1X10
media-ctl -d $M -l '"msm_csiphy0":1->"msm_csid0":0[1], "msm_csid0":1->"msm_vfe0_rdi0":0[1]'
for e in "\"$SN\":0" '"msm_csiphy0":0' '"msm_csiphy0":1' '"msm_csid0":0' '"msm_csid0":1' '"msm_vfe0_rdi0":0' '"msm_vfe0_rdi0":1'; do
  media-ctl -d $M -V "$e[fmt:$F/${W}x$H field:none]"
done
v4l2-ctl -d $V --set-fmt-video=width=$W,height=$H,pixelformat=Y10P
v4l2-ctl -d $S --set-ctrl $AE=1
v4l2-ctl -d $S --set-ctrl exposure=$EXP,analogue_gain=0
# unlit reference
timeout -k 2 8 v4l2-ctl -d $V --stream-mmap=4 --stream-skip=5 --stream-count=2 --stream-to=$O/dark.raw
trap - EXIT INT TERM
sh $T/ir-lit.sh $O $EXP "$GAINS"
v4l2-ctl -d $S -C exposure,analogue_gain
ls -la $O/*.raw
cat /sys/class/leds/*/flash_fault 2>/dev/null
dmesg | tail -n +$N0 | grep -iE 'flash|led|vd55g1|fault' | tail -20
