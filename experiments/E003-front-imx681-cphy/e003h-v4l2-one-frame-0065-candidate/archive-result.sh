#!/bin/bash
set -euo pipefail
STATUS=${1:-unknown}
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-v4l2-one-frame-0065-candidate
DIAG=/sys/bus/platform/devices/acb7000.isp/e003h_pix_rtcdm_diag
OUT=$NEW/RUNTIME-V4L2-0065-QC10C.bin
RUN=$NEW/RUNTIME-V4L2-0065-RUN.txt
POST=$NEW/RUNTIME-V4L2-0065-POST.txt
DMESG=$NEW/RUNTIME-V4L2-0065-DMESG.txt
HASHES=$NEW/RUNTIME-V4L2-0065-HASHES.txt
STAGES=$NEW/RUNTIME-V4L2-0065-RTCDM-STAGES.txt
{
 echo "STATUS=$STATUS"
 echo "ARCHIVE_TIME=$(date -Ins)"
 echo -n 'LIVE_DIAG='; cat "$DIAG" 2>&1 || true
 [ -f "$OUT" ] && stat -c 'QC10C_BYTES=%s' "$OUT" || echo QC10C_OUTPUT=absent
 echo 'WATCHER:'; sudo -n cat "$STAGES" 2>/dev/null || true
} > "$POST"
sudo -n dmesg -T | grep -Ei 'E003h|0065|CSID1|VFE1|RT-CDM|imx681|qcom.*cam|CAMSS|SMMU|IOMMU|panic|oops|SError|BUG:' | tail -n 1400 > "$DMESG" || true
sha256sum "$RUN" "$POST" "$DMESG" > "$HASHES"
sudo -n test -f "$STAGES" && sudo -n sha256sum "$STAGES" >> "$HASHES"
sudo -n test -f "$OUT" && sudo -n sha256sum "$OUT" >> "$HASHES"
sync
echo "ARCHIVED_STATUS=$STATUS"
