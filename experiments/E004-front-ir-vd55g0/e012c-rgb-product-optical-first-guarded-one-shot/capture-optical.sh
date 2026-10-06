#!/usr/bin/env bash
set -Eeuo pipefail
D=/var/lib/sp11-camera-e012c
P=/var/lib/sp11-camera-rgb
[[ "$EUID" == 0 ]]
grep -qw 'sp11_camera_rgb_product=1' /proc/cmdline
[[ ! -e "$P/private-optical/front-current-product-private.png" ]]
[[ ! -e "$P/private-optical/rear-current-product-private.png" ]]
/usr/local/bin/sp11-rgbctl front | tee "$D/FRONT-SELECT.json"
sleep 2
/usr/local/libexec/sp11-camera-stack/rgb/product/private_optical_preview.py --camera front | tee "$D/FRONT-OPTICAL.json"
/usr/local/bin/sp11-rgbctl off | tee "$D/FRONT-OFF.json"
sleep 1
/usr/local/bin/sp11-rgbctl rear | tee "$D/REAR-SELECT.json"
sleep 2
/usr/local/libexec/sp11-camera-stack/rgb/product/private_optical_preview.py --camera rear | tee "$D/REAR-OPTICAL.json"
/usr/local/bin/sp11-rgbctl off | tee "$D/REAR-OFF.json"
/usr/local/bin/sp11-rgbctl status | tee "$D/PRODUCT-STATUS-AFTER-OPTICAL.json"
systemctl stop sp11-camera-rgb.service
for p in "$P/private-optical/front-current-product-private.png" "$P/private-optical/rear-current-product-private.png"; do [[ -f "$p" && ! -L "$p" && "$(stat -c '%U:%G:%a' "$p")" == root:root:600 ]]; done
python3 - <<'PY'
from PIL import Image
from pathlib import Path
for n,s in [('front',(1920,1080)),('rear',(3840,2160))]:
 p=Path('/var/lib/sp11-camera-rgb/private-optical')/(n+'-current-product-private.png')
 with Image.open(p) as im: assert im.format=='PNG' and im.mode=='RGB' and im.size==s
print('E012C_OPTICAL_FILES=PASS FRONT=1920x1080 REAR=3840x2160 PRIVATE=0600')
PY
echo E012C_OPTICAL_CAPTURE=PASS SOAK_STARTED=NO
