#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/eq-bounded-live-r5-r9-runtime
O=$D/runtime-output
{
 echo "STATUS=${1:-unknown}"; echo "TIME=$(date -Ins)"
 for i in 0 1 2 3 4 5; do for p in QC10C TLBG STATS3A; do f="$O/$p-$i.bin"; sudo -n test -f "$f" && sudo -n stat -c "${p}${i}_BYTES=%s" "$f" || echo "${p}${i}=absent"; done; done
} > "$D/POST.txt"
sudo -n dmesg -T | grep -Ei 'AM request controls|E003h|E003i|CSID1|VFE1|RT-CDM|imx681|CAMSS|SMMU|IOMMU|panic|oops|BUG:' | tail -n 3500 > "$D/DMESG.txt" || true
grep -F 'AM request controls:' "$D/DMESG.txt" > "$O/CONTROL-TRANSACTION.txt" || true
sync
echo "ARCHIVED=${1:-unknown}"
