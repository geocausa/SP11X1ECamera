#!/usr/bin/env bash
set -Eeuo pipefail
D=/var/lib/sp11-camera-e012g
P=/var/lib/sp11-camera-rgb
[[ "$EUID" == 0 ]]; grep -qw 'sp11_camera_rgb_product=1' /proc/cmdline
cleanup(){
  python3 "$D/rear-exposure-ladder.py" restore >"$D/REAR-RESTORE-FINALLY.json" 2>"$D/REAR-RESTORE-FINALLY.err" || true
  /usr/local/bin/sp11-rgbctl off >"$D/REAR-OFF-FINALLY.json" 2>/dev/null || true
  systemctl stop sp11-camera-rgb.service >/dev/null 2>&1 || true
}
trap cleanup EXIT
/usr/local/bin/sp11-rgbctl rear | tee "$D/REAR-SELECT.json"
sleep 2
python3 "$D/rear-exposure-ladder.py" run | tee "$D/REAR-EXPOSURE-LADDER.json"
sleep 1
/usr/local/libexec/sp11-camera-stack/rgb/product/private_optical_preview.py --camera rear | tee "$D/REAR-OPTICAL-LADDER.json"
p="$P/private-optical/rear-current-product.png"
[[ -f "$p" && ! -L "$p" && "$(stat -c '%U:%G:%a' "$p")" == root:root:600 ]]
python3 - <<'PY'
from PIL import Image
from pathlib import Path
p=Path('/var/lib/sp11-camera-rgb/private-optical/rear-current-product.png')
with Image.open(p) as im:
 assert im.format=='PNG' and im.mode=='RGB' and im.size==(3840,2160)
 g=im.convert('L');h=g.histogram();n=sum(h)
 def q(f):
  t=int((n-1)*f);c=0
  for i,v in enumerate(h):
   c+=v
   if c>t:return i
 print('E012G_RENDER mean=%.3f p50=%d p95=%d p99=%d max=%d ge96=%.6f' %
       (sum(i*c for i,c in enumerate(h))/n,q(.5),q(.95),q(.99),g.getextrema()[1],sum(h[96:])/n))
PY
python3 "$D/rear-exposure-ladder.py" restore | tee "$D/REAR-RESTORE.json"
/usr/local/bin/sp11-rgbctl off | tee "$D/REAR-OFF.json"
/usr/local/bin/sp11-rgbctl status | tee "$D/PRODUCT-STATUS-AFTER-OPTICAL.json"
systemctl stop sp11-camera-rgb.service
trap - EXIT
echo E012G_REAR_LADDER_OPTICAL_CAPTURE=PASS SOAK_STARTED=NO
