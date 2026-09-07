#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
B=$R/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/ak-bounded-imx681-control-runtime
AE=$BASE/ae-bounded-live-trigger-iq-producer
O=$D/runtime-output
mkdir -p "$O/producer"
gcc -O2 -std=c11 -Wall -Wextra -Werror "$AE/e003i-ae-six-frame-live-iq.c" -o "$O/e003i-ak-six-frame-live-iq"
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
python3 "$BASE/e-template-free-capsule/build-template-free-0076-capsules.py" --output-dir "$T/caps" --manifest "$T/manifest.json" > "$O/TEMPLATE-FREE-R4.log"
cp "$T/caps/E003I_TEMPLATE_FREE_R4.bin" "$O/R4-bootstrap.bin"
sha256sum "$O/R4-bootstrap.bin" > "$O/R4-bootstrap.sha256"
grep -q '^1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa ' "$O/R4-bootstrap.sha256"
sudo -n "$B/setup-pix-media.sh" /dev/media0 > "$O/MEDIA.txt"
V=$(sed -n 's/^VIDEO=//p' "$O/MEDIA.txt" | tail -1); test -c "$V"
SENSOR=$(sed -n 's/^SENSOR=//p' "$O/MEDIA.txt" | tail -1); test -n "$SENSOR"
SUBDEV=$(media-ctl -d /dev/media0 -e "$SENSOR" | tail -1); test -c "$SUBDEV"
v4l2-ctl -d "$SUBDEV" --list-ctrls > "$O/CONTROLS-BEFORE.txt"
for n in vertical_blanking exposure analogue_gain digital_gain; do grep -q "$n" "$O/CONTROLS-BEFORE.txt" || { echo "FAIL: missing control $n" >&2; exit 1; }; done
# Cache a small non-default request while the runtime-PM sensor is off.
v4l2-ctl -d "$SUBDEV" --set-ctrl=exposure=3500,analogue_gain=64,digital_gain=272
v4l2-ctl -d "$SUBDEV" --get-ctrl=vertical_blanking,exposure,analogue_gain,digital_gain > "$O/CONTROLS-AFTER.txt"
grep -Eq '^vertical_blanking: 1394$' "$O/CONTROLS-AFTER.txt"
grep -Eq '^exposure: 3500$' "$O/CONTROLS-AFTER.txt"
grep -Eq '^analogue_gain: 64$' "$O/CONTROLS-AFTER.txt"
grep -Eq '^digital_gain: 272$' "$O/CONTROLS-AFTER.txt"
sudo -n python3 - "$V" <<'PYO'
import os,sys
fd=os.open(sys.argv[1],os.O_RDWR|os.O_CLOEXEC);os.close(fd)
PYO
printf 'STATUS=PASS\nVIDEO=%s\nSENSOR=%s\nSUBDEV=%s\nTARGET_FLL=3554\nTARGET_EXPOSURE=3500\nTARGET_AGAIN=64\nTARGET_DGAIN=272\n' "$V" "$SENSOR" "$SUBDEV" > "$O/CAPTURE-PREFLIGHT.txt"
echo "PASS: AK media/controls prepared VIDEO=$V SUBDEV=$SUBDEV"
