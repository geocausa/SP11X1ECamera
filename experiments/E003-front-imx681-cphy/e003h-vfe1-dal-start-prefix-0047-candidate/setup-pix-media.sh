#!/bin/bash
set -euo pipefail
MEDIA=${1:-/dev/media0}
P=$(media-ctl -d "$MEDIA" -p)
SENSOR=$(printf '%s\n' "$P" | sed -nE 's/^- entity [0-9]+: (imx681 [^ ]+) \(.*/\1/p' | head -1)
[ -n "$SENSOR" ] || { echo 'FAIL: IMX681 entity not found' >&2; exit 1; }
media-ctl -d "$MEDIA" -l '"msm_csiphy2":1 -> "msm_csid1":0 [1]'
media-ctl -d "$MEDIA" -l '"msm_csid1":4 -> "msm_vfe1_pix":0 [1]'
for E in "$SENSOR:0" 'msm_csiphy2:0' 'msm_csiphy2:1' 'msm_csid1:0' 'msm_csid1:4' 'msm_vfe1_pix:0' 'msm_vfe1_pix:1'; do
  N=${E%:*}; PAD=${E##*:}
  media-ctl -d "$MEDIA" -V "\"$N\":$PAD [fmt:SRGGB10_1X10/3840x2640 field:none]"
done
VIDEO=$(media-ctl -d "$MEDIA" -e 'msm_vfe1_video3')
[ -c "$VIDEO" ] || { echo "FAIL: VFE1 PIX video node not found: $VIDEO" >&2; exit 1; }
echo "SENSOR=$SENSOR"
echo "VIDEO=$VIDEO"
media-ctl -d "$MEDIA" -p | grep -E -A8 -B3 'imx681|msm_csiphy2|msm_csid1|msm_vfe1_pix|msm_vfe1_video3'
