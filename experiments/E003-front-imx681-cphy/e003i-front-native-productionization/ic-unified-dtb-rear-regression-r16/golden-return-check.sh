#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/ic-unified-dtb-rear-regression-r16
"$R/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process
! grep -Fq 'sp11_camera_ic_unified_rear_r16=1' /proc/cmdline
ENV=$(sudo -n grub-editenv /boot/grub/grubenv list 2>/dev/null||true); grep -qx 'saved_entry=sp11-audio-fullio-v19c'<<<"$ENV"; ! grep -q '^next_entry=.'<<<"$ENV"
{ echo 'schema=sp11-camera-ic-golden-return-v1'; echo 'status=PASS'; echo "time=$(date -Ins)"; echo "boot_id=$(cat /proc/sys/kernel/random/boot_id)"; } > "$D/GOLDEN-RETURN.txt"
echo 'IC_GOLDEN_RETURN=PASS'
