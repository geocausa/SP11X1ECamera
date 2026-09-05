#!/bin/bash
set -euo pipefail
D=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/s-bounded-live-tlbg-runtime
{
 echo "STATUS=${1:-unknown}"; echo "TIME=$(date -Ins)"
 for i in 0 1 2 3 4 5; do
   for p in QC10C TLBG; do f="$D/$p-$i.bin"; sudo -n test -f "$f" && sudo -n stat -c "${p}${i}_BYTES=%s" "$f" || echo "${p}${i}=absent"; done
 done
} > "$D/POST.txt"
sudo -n dmesg -T | grep -Ei 'E003h|E003i|CSID1|VFE1|RT-CDM|imx681|CAMSS|SMMU|IOMMU|panic|oops|BUG:' | tail -n 3000 > "$D/DMESG.txt" || true
sha256sum "$D"/RUN.txt "$D"/POST.txt "$D"/DMESG.txt "$D"/QC10C-*.bin "$D"/TLBG-*.bin 2>/dev/null | sort > "$D/HASHES.txt" || true
sync
echo "ARCHIVED=${1:-unknown}"
