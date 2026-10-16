#!/bin/sh
# sp11-imx681-lab boot only. Load camss 50 + Peter's vd55g1 debug build once, then try several sensor configs.
# Each config line: name|fw_file|oif_override|skip_isl|extra
O=${OUT:-/root/imx681-test/irM}; rm -rf $O; mkdir -p $O; exec > $O/log.txt 2>&1
D=/var/lib/sp11-camera-daily2; T=/root/imx681-test; P=/sys/module/vd55g1/parameters
grep -q sp11-imx681-lab /proc/cmdline || { echo 'not the lab boot'; exit 1; }
for m in i2c_qcom_cci mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg videobuf2_vmalloc v4l2_cci; do modprobe $m; done
insmod $D/modules/qcom-camss.ko $(cat $D/camss-params.txt)
insmod $D/modules/imx681.ko
insmod $T/ovmod/ov13858.ko
insmod $T/vddbg/vd55g1.ko
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
while IFS='|' read name fw oif isl ex; do
  [ -z "$name" ] && continue
  echo "===== $name fw=$fw oif=$oif skip_isl=$isl extra=$ex"
  sleep 6   # let runtime PM power the sensor off so the next power-on re-patches
  if [ -n "$fw" ]; then printf %s "$fw"; else printf "\\000"; fi > $P/fw_file; echo $oif > $P/oif_override; echo $isl > $P/skip_isl
  if [ -n "$ex" ]; then echo "$ex" > $P/extra; else echo 0 > $P/extra; fi
  timeout -k 2 8 v4l2-ctl -d $V --stream-mmap=4 --stream-skip=5 --stream-count=3 --stream-to=$O/$name.raw
  echo "capture rc=$? bytes=$(stat -c %s $O/$name.raw 2>/dev/null)"
  dmesg | tail -n +$N0 | grep -E 'vd55g1|camss|csid|vfe' | grep -v -E '^\[ *[0-9.]+\]  ' | tail -12
  N0=$(dmesg | wc -l)
done <<'EOF'
st_1200_oif||-1|1|0x0300b0,0x030104
st_1128_noisl||-1|1|
EOF
echo done
