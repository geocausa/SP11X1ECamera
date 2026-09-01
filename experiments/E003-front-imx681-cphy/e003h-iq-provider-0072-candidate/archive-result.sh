#!/bin/bash
set -euo pipefail
STATUS=${1:-unknown}
NEW=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera/experiments/E003-front-imx681-cphy/e003h-iq-provider-0072-candidate
DIAG=/sys/bus/platform/devices/acb7000.isp/e003h_pix_rtcdm_diag
RUN=$NEW/RUNTIME-V4L2-0072-RUN.txt; POST=$NEW/RUNTIME-V4L2-0072-POST.txt; DMESG=$NEW/RUNTIME-V4L2-0072-DMESG.txt; HASHES=$NEW/RUNTIME-V4L2-0072-HASHES.txt; STAGES=$NEW/RUNTIME-V4L2-0072-RTCDM-STAGES.txt
{
 echo "STATUS=$STATUS"; echo "ARCHIVE_TIME=$(date -Ins)"; echo -n 'LIVE_DIAG='; cat "$DIAG" 2>&1 || true
 for i in 0 1 2 3 4; do f="$NEW/RUNTIME-V4L2-0072-QC10C-$i.bin"; [ -f "$f" ] && stat -c "QC10C${i}_BYTES=%s" "$f" || echo "QC10C${i}_OUTPUT=absent"; done
 echo 'WATCHER:'; sudo -n cat "$STAGES" 2>/dev/null || true
} > "$POST"
sudo -n dmesg -T | grep -Ei 'E003h|0072|CSID1|VFE1|RT-CDM|imx681|qcom.*cam|CAMSS|SMMU|IOMMU|panic|oops|SError|BUG:' | tail -n 1800 > "$DMESG" || true
sha256sum "$RUN" "$POST" "$DMESG" > "$HASHES"; sudo -n test -f "$STAGES" && sudo -n sha256sum "$STAGES" >> "$HASHES"
for i in 0 1 2 3 4; do f="$NEW/RUNTIME-V4L2-0072-QC10C-$i.bin"; sudo -n test -f "$f" && sudo -n sha256sum "$f" >> "$HASHES"; done
sync; echo "ARCHIVED_STATUS=$STATUS"
