#!/bin/sh
# Lab boot only. Reload the camera modules with a chosen ov13858.ko and capture raw RDI frames
# from the rear camera: ov13858 -> msm_csiphy1 -> msm_csid0 -> msm_vfe0_rdi0.
# Usage: lab-rear.sh <ov13858.ko> <W> <H> <out-dir> [exposure] [again]   (EXTRA/PRE: more controls)
KO=$1; W=$2; H=$3; O=$4; EXP=${5:-2000}; AG=${6:-256}
D=/var/lib/sp11-camera-daily2
mkdir -p $O; exec > $O/log.txt 2>&1
set -x
grep -q sp11-imx681-lab /proc/cmdline || { echo 'not the lab boot'; exit 1; }
pkill v4l2-ctl; sleep 1
rmmod sp11_vd55g0 ov13858 imx681 qcom_camss 2>/dev/null
for m in i2c_qcom_cci mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg videobuf2_vmalloc v4l2_cci; do modprobe $m; done
N0=$(dmesg | wc -l)
insmod $D/modules/qcom-camss.ko $(cat $D/camss-params.txt)
insmod $D/modules/imx681.ko
insmod $KO
insmod $D/modules/sp11-vd55g0.ko
sleep 3
M=$(for m in /dev/media*; do media-ctl -d $m -p 2>/dev/null | grep -q msm_csid0 && echo $m; done | head -1)
S=$(media-ctl -d $M -e 'ov13858 3-0010')
V=$(media-ctl -d $M -e msm_vfe0_video0)
F=SGRBG10_1X10
media-ctl -d $M -l '"msm_csiphy1":1->"msm_csid0":0[1], "msm_csid0":1->"msm_vfe0_rdi0":0[1]'
for e in '"ov13858 3-0010":0' '"msm_csiphy1":0' '"msm_csiphy1":1' '"msm_csid0":0' '"msm_csid0":1' '"msm_vfe0_rdi0":0' '"msm_vfe0_rdi0":1'; do
  media-ctl -d $M -V "$e[fmt:$F/${W}x$H field:none]"
done
media-ctl -d $M -p | grep -A4 -E 'entity.*(ov13858|msm_csiphy1|msm_csid0 |msm_vfe0_rdi0)' | grep -E 'entity|fmt'
v4l2-ctl -d $V --set-fmt-video=width=$W,height=$H,pixelformat=pgAA
v4l2-ctl -d $V --get-fmt-video | grep -E 'Width|Bytes|Size'
[ -n "$PRE" ] && v4l2-ctl -d $S --set-ctrl $PRE
v4l2-ctl -d $S --set-ctrl exposure=$EXP,analogue_gain=$AG${EXTRA:+,$EXTRA}
v4l2-ctl -d $S --list-ctrls
timeout 12 v4l2-ctl -d $V --stream-mmap=4 --stream-skip=15 --stream-count=3 --stream-to=$O/raw.bin
echo "capture rc=$?"
ls -la $O/raw.bin
timeout 8 v4l2-ctl -d $V --stream-mmap=4 --stream-count=60 2>&1 | tail -2
dmesg | tail -n +$N0 | grep -v -E '^\[ *[0-9.]+\]  |x[0-9]+ ?:|Modules linked|Tainted|Hardware name|pstate|pc :|lr :|sp :|end trace|vd55g0|imx681' | tail -30
