#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/ek-linux-front-awb-otp-read-gate
OUT=$D/runtime-output
"$D/runtime-preflight.sh"
mkdir -p "$OUT"
BEFORE=$(date '+%s')
for m in mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg v4l2_cci; do sudo -n modprobe "$m"; done
sudo -n insmod "$BASE/z-live-3a-runtime/qcom-camss-e003i-y.ko"
sudo -n insmod "$D/imx681.ko"
sudo -n dmesg > "$OUT/DMESG.txt"
LINE=$(grep 'SP11 EK AWB OTP 0x0941..0x094c:' "$OUT/DMESG.txt" | tail -1 || true)
[ -n "$LINE" ] || { echo 'FAIL: EK OTP log absent' >&2; exit 1; }
printf '%s\n' "$LINE" > "$OUT/OTP-LINE.txt"
python3 - "$OUT/OTP-LINE.txt" "$BASE/ei-front-awb-otp-oracle/AWB-OTP-RAW.bin" <<'PY'
import re,sys,hashlib
from pathlib import Path
line=Path(sys.argv[1]).read_text()
m=re.search(r'0x0941\.\.0x094c:\s*((?:[0-9a-fA-F]{2}[ -]?){12})',line)
if not m: raise SystemExit('FAIL: cannot parse OTP line')
h=re.findall(r'[0-9a-fA-F]{2}',m.group(1)); got=bytes.fromhex(' '.join(h)); exp=Path(sys.argv[2]).read_bytes()
if got!=exp: raise SystemExit(f'FAIL: OTP mismatch got={got.hex()} expected={exp.hex()}')
print('PASS OTP='+got.hex(' ')+' SHA256='+hashlib.sha256(got).hexdigest())
PY
! grep -Eq 'MODE_SELECT=1|front transmission started|STREAMON' "$OUT/DMESG.txt" || { echo 'FAIL: stream activity detected' >&2; exit 1; }
{
 echo 'schema=sp11-e003i-ek-live-v1'; echo 'status=PASS_LINUX_PHYSICAL_OTP_READ'; echo "time=$(date -Ins)"; echo "$LINE";
 sha256sum "$BASE/ei-front-awb-otp-oracle/AWB-OTP-RAW.bin";
} > "$OUT/RESULT.txt"
echo 'PASS: Linux physical front AWB OTP matches EI exactly; no stream requested'
