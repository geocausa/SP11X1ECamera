#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
B=$R/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/db-bounded-native-aec-sensor-loop
O=$D/runtime-output
mkdir -p "$O/producer"
"$D/build-helper.sh" "$O/e003i-db-six-frame-native-aec"
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
python3 "$BASE/e-template-free-capsule/build-template-free-0076-capsules.py" --output-dir "$T/caps" --manifest "$T/manifest.json" > "$O/TEMPLATE-FREE-R4.log"
cp "$T/caps/E003I_TEMPLATE_FREE_R4.bin" "$O/R4-bootstrap.bin"
sha256sum "$O/R4-bootstrap.bin" > "$O/R4-bootstrap.sha256"
grep -q '^1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa ' "$O/R4-bootstrap.sha256"
sudo -n "$B/setup-pix-media.sh" /dev/media0 > "$O/MEDIA.txt"
V=$(sed -n 's/^VIDEO=//p' "$O/MEDIA.txt" | tail -1); test -c "$V"
SENSOR=$(sed -n 's/^SENSOR=//p' "$O/MEDIA.txt" | tail -1); test -n "$SENSOR"
SUBDEV=$(sudo -n media-ctl -d /dev/media0 -e "$SENSOR" | tail -1); test -c "$SUBDEV"
sudo -n v4l2-ctl -d "$SUBDEV" --list-ctrls > "$O/CONTROLS-BEFORE.txt"
for n in vertical_blanking exposure analogue_gain digital_gain; do grep -q "$n" "$O/CONTROLS-BEFORE.txt" || { echo "FAIL: missing control $n" >&2; exit 1; }; done
sudo -n v4l2-ctl -d "$SUBDEV" --set-ctrl=vertical_blanking=1402,exposure=3554,analogue_gain=0,digital_gain=256
sudo -n v4l2-ctl -d "$SUBDEV" --get-ctrl=vertical_blanking,exposure,analogue_gain,digital_gain > "$O/CONTROLS-AFTER.txt"
for e in 'vertical_blanking: 1402' 'exposure: 3554' 'analogue_gain: 0' 'digital_gain: 256'; do grep -Fxq "$e" "$O/CONTROLS-AFTER.txt"; done
printf 'STATUS=PASS\nVIDEO=%s\nSENSOR=%s\nSUBDEV=%s\nBOOTSTRAP_FLL=3562\nBOOTSTRAP_VBLANK=1402\nBOOTSTRAP_EXPOSURE=3554\nBOOTSTRAP_AGAIN=0\nBOOTSTRAP_DGAIN=256\n' "$V" "$SENSOR" "$SUBDEV" > "$O/CAPTURE-PREFLIGHT.txt"
echo "PASS: DB media/DA-bootstrap prepared VIDEO=$V SUBDEV=$SUBDEV"
