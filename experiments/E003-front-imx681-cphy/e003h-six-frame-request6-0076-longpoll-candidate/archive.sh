#!/bin/bash
set -euo pipefail
D=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0076-longpoll-candidate
{
 echo "STATUS=${1:-unknown}"; echo "TIME=$(date -Ins)"; echo -n 'RTCDM='; cat /sys/bus/platform/devices/acb7000.isp/e003h_pix_rtcdm_diag 2>&1 || true
 for i in 0 1 2 3 4 5; do f="$D/QC10C-$i.bin"; sudo -n test -f "$f" && sudo -n stat -c "QC10C${i}_BYTES=%s" "$f" || echo "QC10C${i}=absent"; done
 echo 'WATCHER:'; sudo -n cat "$D/RTCDM-STAGES.txt" 2>/dev/null || true
} > "$D/POST.txt"
sudo -n dmesg -T | grep -Ei 'E003h|0074|0076|CSID1|VFE1|RT-CDM|imx681|CAMSS|SMMU|IOMMU|panic|oops|BUG:' | tail -n 2600 > "$D/DMESG.txt" || true
sha256sum "$D"/RUN.txt "$D"/POST.txt "$D"/DMESG.txt "$D"/QC10C-*.bin 2>/dev/null | sort > "$D/HASHES.txt" || true
sync
echo "ARCHIVED=${1:-unknown}"
