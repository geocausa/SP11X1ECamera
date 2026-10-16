#!/bin/sh
# After lab-ir-flash.sh has set up the pipeline in this boot: lit captures with the LED armed only during capture.
# Usage: ir-lit.sh <out-dir> <exposure-lines> <gain list>
O=$1; EXP=$2; GAINS=$3; T=/root/imx681-test
M=/dev/media0; S=$(media-ctl -d $M -e 'vd55g1 2-0060'); FL=$(media-ctl -d $M -e 'sp11-ir-illuminator'); V=$(media-ctl -d $M -e msm_vfe0_video0)
mkdir -p $O; exec >> $O/log.txt 2>&1
set -x
v4l2-ctl -d $S --set-ctrl auto_exposure=1
for g in $GAINS; do
  v4l2-ctl -d $S --set-ctrl exposure=$EXP,analogue_gain=$g
  v4l2-ctl -d $S --set-ctrl led_mode=1
  python3 $T/flash-hold.py $FL 10000 200000 -- timeout -k 2 8 v4l2-ctl -d $V --stream-mmap=4 --stream-skip=8 --stream-count=3 --stream-to=$O/lit-e$EXP-g$g.raw
  echo "capture e=$EXP g=$g rc=$?"
  v4l2-ctl -d $S --set-ctrl led_mode=0
  sleep 1
done
v4l2-ctl -d $FL -C led_mode,strobe_source,faults
ls -la $O/*.raw
dmesg | grep -iE 'flash|illum|vd55g1' | tail -5
