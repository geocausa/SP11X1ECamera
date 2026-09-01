#!/bin/bash
set -euo pipefail
STATUS=${1:-unknown}
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-slot-lifetime-0067-candidate
DIAG=/sys/bus/platform/devices/acb7000.isp/e003h_pix_rtcdm_diag
OUT0=$NEW/RUNTIME-V4L2-0067-QC10C-0.bin
OUT1=$NEW/RUNTIME-V4L2-0067-QC10C-1.bin
RUN=$NEW/RUNTIME-V4L2-0067-RUN.txt
POST=$NEW/RUNTIME-V4L2-0067-POST.txt
DMESG=$NEW/RUNTIME-V4L2-0067-DMESG.txt
HASHES=$NEW/RUNTIME-V4L2-0067-HASHES.txt
STAGES=$NEW/RUNTIME-V4L2-0067-RTCDM-STAGES.txt
{
 echo "STATUS=$STATUS"
 echo "ARCHIVE_TIME=$(date -Ins)"
 echo -n 'LIVE_DIAG='; cat "$DIAG" 2>&1 || true
 [ -f "$OUT0" ] && stat -c 'QC10C0_BYTES=%s' "$OUT0" || echo QC10C0_OUTPUT=absent
 [ -f "$OUT1" ] && stat -c 'QC10C1_BYTES=%s' "$OUT1" || echo QC10C1_OUTPUT=absent
 echo 'WATCHER:'; sudo -n cat "$STAGES" 2>/dev/null || true
} > "$POST"
sudo -n dmesg -T | grep -Ei 'E003h|0067|CSID1|VFE1|RT-CDM|imx681|qcom.*cam|CAMSS|SMMU|IOMMU|panic|oops|SError|BUG:' | tail -n 1600 > "$DMESG" || true
sha256sum "$RUN" "$POST" "$DMESG" > "$HASHES"
sudo -n test -f "$STAGES" && sudo -n sha256sum "$STAGES" >> "$HASHES"
sudo -n test -f "$OUT0" && sudo -n sha256sum "$OUT0" >> "$HASHES"
sudo -n test -f "$OUT1" && sudo -n sha256sum "$OUT1" >> "$HASHES"
sync
echo "ARCHIVED_STATUS=$STATUS"
