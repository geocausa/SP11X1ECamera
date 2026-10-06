#!/usr/bin/env bash
set -Eeuo pipefail
D=/var/lib/sp11-camera-e012f
P=/var/lib/sp11-camera-rgb
[[ "$EUID" == 0 ]]; grep -qw 'sp11_camera_rgb_product=1' /proc/cmdline
# Tonight's Windows baseline proved the front scene is genuinely dark; isolate rear first.
/usr/local/bin/sp11-rgbctl rear | tee "$D/REAR-SELECT.json"
sleep 2
python3 "$D/rear-profile.py" status | tee "$D/REAR-PROFILE-BASELINE.json"
python3 "$D/rear-profile.py" apply | tee "$D/REAR-PROFILE-APPLY.json"
sleep 2
/usr/local/libexec/sp11-camera-stack/rgb/product/private_optical_preview.py --camera rear | tee "$D/REAR-OPTICAL-FIXED-PROFILE.json"
python3 "$D/rear-profile.py" restore | tee "$D/REAR-PROFILE-RESTORE.json"
/usr/local/bin/sp11-rgbctl off | tee "$D/REAR-OFF.json"
/usr/local/bin/sp11-rgbctl status | tee "$D/PRODUCT-STATUS-AFTER-OPTICAL.json"
systemctl stop sp11-camera-rgb.service
p="$P/private-optical/rear-current-product-private.png"
[[ -f "$p" && ! -L "$p" && "$(stat -c '%U:%G:%a' "$p")" == root:root:600 ]]
python3 - <<'PY'
from PIL import Image,ImageStat
from pathlib import Path
p=Path('/var/lib/sp11-camera-rgb/private-optical/rear-current-product-private.png')
with Image.open(p) as im:
 assert im.format=='PNG' and im.mode=='RGB' and im.size==(3840,2160)
 g=im.convert('L'); h=g.histogram(); n=sum(h); s=sum(i*c for i,c in enumerate(h))/n
 def q(frac):
  target=int((n-1)*frac); c=0
  for i,v in enumerate(h):
   c+=v
   if c>target:return i
 print(f'E012F_REAR_RGB mean={s:.3f} p50={q(.5)} p95={q(.95)} p99={q(.99)} max={g.getextrema()[1]}')
PY
echo E012F_REAR_FIXED_PROFILE_OPTICAL_CAPTURE=PASS SOAK_STARTED=NO
