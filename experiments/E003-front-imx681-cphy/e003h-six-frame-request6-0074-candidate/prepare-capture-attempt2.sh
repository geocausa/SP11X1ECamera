#!/bin/bash
set -euo pipefail
NEW=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate
MEDIA=/dev/media0
LOG=$NEW/RUNTIME-V4L2-0074-A2-MEDIA.txt
PREF=$NEW/ATTEMPT2-CAPTURE-PREFLIGHT.txt
DIAG=/sys/bus/platform/devices/acb7000.isp/e003h_pix_rtcdm_diag
fail(){ echo "FAIL: $*" >&2; exit 1; }
sudo -n true || fail sudo_noninteractive
[ -d /sys/module/qcom_camss ] && [ -d /sys/module/imx681 ] || fail modules
sudo -n test -r "$MEDIA" -a -w "$MEDIA" || fail media_permissions
sudo -n "$NEW/setup-pix-media.sh" "$MEDIA" >"$LOG"
VIDEO=$(sed -n 's/^VIDEO=//p' "$LOG" | tail -1)
[ -n "$VIDEO" ] && [ -c "$VIDEO" ] || fail video_resolution
sudo -n test -r "$VIDEO" -a -w "$VIDEO" || fail video_permissions
sudo -n python3 - "$VIDEO" <<'PY'
import os,sys
fd=os.open(sys.argv[1],os.O_RDWR|os.O_CLOEXEC)
os.close(fd)
PY
D=$(cat "$DIAG")
case "$D" in
  *'seq=0 stage=0 name=idle fifo_seq=0'*'error=0'*'faulted=0'*) ;;
  *) echo "FAIL: RT-CDM not pristine: $D" >&2; exit 1;;
esac
{
 echo 'STATUS=PASS'
 echo "TIME=$(date -Ins)"
 echo 'SUDO_NONINTERACTIVE=true'
 echo "MEDIA=$MEDIA"
 echo 'MEDIA_ROOT_RW=true'
 echo "VIDEO=$VIDEO"
 echo 'VIDEO_ROOT_RW=true'
 echo 'VIDEO_ROOT_OPEN_RDWR=true'
 echo "RTCDM=$D"
 echo 'STREAMON_INVOCATIONS=0'
 echo 'HELPER_INVOCATIONS=0'
} >"$PREF"
echo "PASS: attempt2 privileged media/open preflight complete; VIDEO=$VIDEO; RT-CDM idle"
