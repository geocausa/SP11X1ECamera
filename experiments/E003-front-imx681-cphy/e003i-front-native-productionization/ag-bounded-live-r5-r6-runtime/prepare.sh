#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
B=$R/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/ag-bounded-live-r5-r6-runtime
AE=$BASE/ae-bounded-live-trigger-iq-producer
O=$D/runtime-output
mkdir -p "$O/producer"
# Build the capture helper before any stream.
gcc -O2 -std=c11 -Wall -Wextra -Werror "$AE/e003i-ae-six-frame-live-iq.c" -o "$O/e003i-ag-six-frame-live-iq"
# Generate R4 from the template-free composer; R5/R6 temp products are deleted and cannot be used by invoke-once.
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
python3 "$BASE/e-template-free-capsule/build-template-free-0076-capsules.py" --output-dir "$T/caps" --manifest "$T/manifest.json" > "$O/TEMPLATE-FREE-R4.log"
cp "$T/caps/E003I_TEMPLATE_FREE_R4.bin" "$O/R4-bootstrap.bin"
sha256sum "$O/R4-bootstrap.bin" > "$O/R4-bootstrap.sha256"
grep -q '^1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa ' "$O/R4-bootstrap.sha256"
# Configure the proven front-only media graph and prove the fd can be opened.
sudo -n "$B/setup-pix-media.sh" /dev/media0 > "$O/MEDIA.txt"
V=$(sed -n 's/^VIDEO=//p' "$O/MEDIA.txt" | tail -1); test -c "$V"
sudo -n python3 - "$V" <<'PYO'
import os,sys
fd=os.open(sys.argv[1],os.O_RDWR|os.O_CLOEXEC);os.close(fd)
PYO
printf 'STATUS=PASS\nVIDEO=%s\n' "$V" > "$O/CAPTURE-PREFLIGHT.txt"
echo "PASS: AG helper/template-free-R4/media prepared VIDEO=$V"
